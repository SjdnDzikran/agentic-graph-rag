import pandas as pd
from sentence_transformers import SentenceTransformer

def build_embeddings(input_csv=r"C:\Project\agentic-graph-rag\data\cve_dataset.csv",
                     output_json=r"C:\Project\agentic-graph-rag\data\cve_with_embeddings.json"):
    df = pd.read_csv(input_csv)

    model = SentenceTransformer("all-MiniLM-L6-v2")

    df["embedding"] = df["description"].apply(lambda x: model.encode(x).tolist())

    df.to_json(output_json, orient="records", indent=2)

if __name__ == "__main__":
    build_embeddings()
