import json
import textwrap
import time

import ollama
from loguru import logger
from sqlalchemy import Engine, text

from src.core.config import MAX_DB_ATTEMPTS


def faithfulness(eval_dict: dict[str, str], eval_model: str) -> dict:
    system_prompt = textwrap.dedent("""
            ### Goal: 
            Detect hallucinations. This prompt forces the model to extract claims and verify them individually against the context.

            ### INSTRUCTIONS:
            You are an expert factual auditor. Your task is to determine if the Agent Answer is strictly derived from the Retrieved Context.
            Return only json with the specified format, no explanations or extra text.

            ### Evaluation Process:
            - Break down the Agent Answer into individual factual claims.
            - For each claim, check if it is directly supported by the Retrieved Context.
            - Ignore your own internal knowledge; rely only on the provided context.

            **Output Format (JSON):**
            {
            "claims_backed_by_context": ["claim 1", "claim 2"],
            "hallucinated_claims": ["list any claim not in context"],
            "score": (1-5),
            "reasoning": "Detailed explanation of why the score was given."
            }

            **Scoring Scale:**
            5: All claims are perfectly supported.
            3: Most claims are supported, but some minor details are missing or slightly inferred.
            1: The answer contains significant hallucinations or information not present in the context.
        """)

    user_prompt = f"""
        Retrieved Context: {eval_dict["rag_context"]}
        Agent Answer: {eval_dict["agent_answer"]}
    """

    llm_output = ollama.chat(
        model=eval_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    return json.loads(llm_output["message"]["content"])


def answer_relevance(eval_dict: dict[str, str], eval_model: str) -> dict:
    system_prompt = textwrap.dedent("""
            ### Goal:
            Ensure the answer directly addresses the user's intent and query without irrelevant filler.

            ### INSTRUCTIONS:
            You are a Customer Experience Quality Evaluator. You will judge how relevant an Agent Answer is to a User Query.
            Return only json with the specified format, no explanations or extra text.

            ### Evaluation Process:
            - Analyze the core intent of the User Query.
            - Evaluate if the Agent Answer provides a direct solution or information requested.
            - Check for brevity and clarity; identify if the answer includes redundant or off-topic information.

            **Output Format (JSON):**
            {{
            "user_intent_identified": "Short description of what the user is actually looking for",
            "missing_key_points": ["list any part of the query that was ignored"],
            "score": (1-5),
            "reasoning": "Detailed explanation of why the score was given."
            }}

            **Scoring Scale:**
            5: Perfect alignment; answer is concise and covers all aspects of the query.
            3: Helpful and relevant, but might be too wordy or miss a minor part of the question.
            1: Completely irrelevant, vague, or fails to address the user's query at all.
        """)

    user_prompt = f"""
        User Query: {eval_dict["user_query"]}
        Agent Answer: {eval_dict["agent_answer"]}
    """

    llm_output = ollama.chat(
        model=eval_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    return json.loads(llm_output["message"]["content"])


def context_precision(eval_dict: dict[str, str], eval_model: str) -> dict:
    system_prompt = textwrap.dedent("""
            ### Goal:
            Evaluate the quality of the RAG retrieval step. Determine if the provided context contains the necessary facts.

            ### INSTRUCTIONS:
            You are a Search Quality Engineer. Your task is to evaluate if the Retrieved Context contains the information needed to answer the User Query.
            Return only json with the specified format, no explanations or extra text.

            ### Evaluation Process:
            - Scan the Retrieved Context for specific facts, dates, or names required by the User Query.
            - Identify if the context is sufficient to form a complete and accurate answer.
            - Note if the context is irrelevant or contains "noise" that doesn't help answer the query.

            **Output Format (JSON):**
            {{
            "useful_facts_found": ["fact 1", "fact 2"],
            "missing_information": ["what specific info is missing to answer the query fully?"],
            "score": (1-5),
            "reasoning": "Detailed explanation of why the score was given."
            }}

            **Scoring Scale:**
            5: The context contains all necessary information to provide a definitive answer.
            3: The context is partially relevant; it contains some clues but lacks key details for a full answer.
            1: The context is entirely irrelevant to the user's query.
        """)

    user_prompt = f"""
        User Query: {eval_dict["user_query"]}
        Retrieved Context: {eval_dict["rag_context"]}
    """

    llm_output = ollama.chat(
        model=eval_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    return json.loads(llm_output["message"]["content"])


def get_evaluation_data(eval_engine: Engine) -> list[dict[str, str]]:
    sql = text("""SELECT * FROM evaluation_data""")
    for attempt in range(MAX_DB_ATTEMPTS):
        try:
            with eval_engine.connect() as conn:
                result = conn.execute(sql)
                return [
                    {
                        "user_query": str(row[0]),
                        "rag_context": str(row[1]),
                        "agent_answer": str(row[2]),
                    }
                    for row in result
                ]

        except Exception as e:
            logger.warning(f"Attempts:{attempt}\nError getting eval data: {e}")
            time.sleep(2)
    raise RuntimeError(f"Error getting eval data after {MAX_DB_ATTEMPTS} attempts")


def run_evaluation_pipeline(eval_engine: Engine, eval_model: str) -> None:
    eval_data = get_evaluation_data(eval_engine)

    if not eval_data:
        logger.warning("No evaluation data found in the database.")
        return

    json.dump(
        [
            {
                "faithfulness": faithfulness(eval_dict, eval_model),
                "relevance": answer_relevance(eval_dict, eval_model),
                "context_precision": context_precision(eval_dict, eval_model),
            }
            for eval_dict in eval_data
        ],
        open("scripts/evaluation_results.json", "w"),
        indent=4,
    )
