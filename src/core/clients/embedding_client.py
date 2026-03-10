import gc
import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from transformers import BitsAndBytesConfig
from loguru import logger


class EmbeddingClient:
    def __init__(
        self,
        model_dir: str,
        embedding_model_id: str,
        quant_type: str | None,
        n_batch: int,
        n_ctx: int,
    ):
        self.repo_id = embedding_model_id
        self.quant_type = quant_type
        self.batch_size = n_batch

        # BACKEND AND DTYPE
        if torch.cuda.is_available():
            self.device = "cuda"
            device_name = torch.cuda.get_device_name()
            attn = "sdpa"

            if "RTX 6000" in device_name:
                torch.backends.cuda.matmul.allow_tf32 = True
                torch.backends.cudnn.allow_tf32 = True

                # self.dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
                self.dtype = torch.float16
            elif "GTX 1660" in device_name:
                self.dtype = torch.float16

        elif torch.backends.mps.is_available():
            self.device = "mps"
            self.dtype = torch.float16
            attn = None

        else:
            self.device = "cpu"
            self.dtype = torch.float16
            attn = None


        model_args = {
            "torch_dtype": self.dtype,
            "attn_implementation": attn,
            "trust_remote_code": True,
        }

        # CUDA QUANTIZATION
        if self.device == "cuda" and self.quant_type:
            if self.quant_type == "4bit":
                model_args["quantization_config"] = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=self.dtype,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_use_double_quant=True,
                )
                logger.debug("Using 4-bit (NF4) quantization")
            elif self.quant_type == "8bit":
                model_args["quantization_config"] = BitsAndBytesConfig(
                    load_in_8bit=True
                )
                logger.debug("Using 8-bit quantization")

        logger.info(
            f"Loading SentenceTransformer: {self.repo_id} on {self.device}\nDTYPE={self.dtype}, BATCH_SIZE={self.batch_size}, N_CTX={n_ctx}, "
        )
        self.model = SentenceTransformer(
            self.repo_id,
            device=self.device,
            model_kwargs=model_args,
            cache_folder=model_dir,
        )
        

        # MPS QUANTIZATION
        if self.device == "mps" and self.quant_type:
            from torchao.quantization import (
                quantize_,
                Int4WeightOnlyConfig,
                Int8WeightOnlyConfig
            )

            if self.quant_type == "4bit":
                quantize_(self.model, Int4WeightOnlyConfig(group_size=128))
                logger.info("MPS: Using torchao Int4WeightOnlyConfig(group_size=128)")
            elif self.quant_type == "8bit":
                quantize_(self.model, Int8WeightOnlyConfig())
                logger.info("MPS: Using torchao Int8WeightOnlyConfig")


        self.model.max_seq_length = n_ctx

        # if self.device == "cuda" and hasattr(torch, "compile"):
        #     try:
        #         logger.debug("Compiling model..")
        #         self.model = torch.compile(self.model)
        #         self.model.encode(["Warmup text"], batch_size=1)
        #     except Exception as e:
        #         logger.warning(f"torch.compile skipped: {e}")

        # get VECTOR_DIM
        self.vector_dim = self.model.get_sentence_embedding_dimension()
        if self.vector_dim is None:
            # fallback
            self.vector_dim = len(self.model.encode("test"))

        logger.success(f"EmbeddingClient initialized. VECTOR_DIM={self.vector_dim}")

    def embed_batch(self, contents: list[str]) -> np.ndarray:
        logger.debug(f"EMBEDDING BATCH: size={len(contents)}")

        try:
            with torch.inference_mode():
                embeddings = self.model.encode(
                    contents,
                    batch_size=self.batch_size,
                    normalize_embeddings=True,
                    show_progress_bar=False,
                    convert_to_numpy=True,
                )

            # memory cleanup
            if self.device == "cuda":
                torch.cuda.empty_cache()
            elif self.device == "mps":
                torch.mps.empty_cache()
            gc.collect()

            return embeddings

        except Exception:
            logger.exception("Error during embedding generation")
            raise