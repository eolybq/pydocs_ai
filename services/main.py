from services.create_embeddings import get_embedding
from services.database import create_table

def run_embedding_pipeline(doc_name):
    status_table = create_table(doc_name)
    if status_table["status"] != "success":
        print(f"Failed to create table for {doc_name}: {status_table["error"]}")
        return


    status_embedding = get_embedding(doc_name)
    if status_embedding["status"] == "completed":
        print(f"Embedding pipeline for {doc_name} completed successfully.")
        return
    else:
        print(f"Embedding pipeline for {doc_name} failed with error: {status_embedding["error"]}")
        return



if __name__ == "__main__":
    doc_name = "pandas"
    run_embedding_pipeline(doc_name)