import os
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
from agno.embedder.together import TogetherEmbedder
from tqdm import tqdm

load_dotenv()

embedder = TogetherEmbedder(api_key=os.getenv("TOGETHER_API_KEY"))

csv_path = Path("/home/deb/usr/manimator/backend/data/manim_dataset.csv")
output_path = csv_path.parent / "manim_dataset_with_embeddings.csv"

df = pd.read_csv(csv_path)

if 'prompt' not in df.columns:
    raise ValueError("CSV file must contain a 'prompt' column")

def get_embedding(text):
    try:
        if pd.isna(text) or not str(text).strip():
            return None
        return embedder.get_embedding(str(text))
    except Exception as e:
        print(f"Error generating embedding for text: {text[:100]}... Error: {str(e)}")
        return None

print("Generating embeddings for prompts...")

tqdm.pandas(desc="Processing prompts")
df['embeddings'] = df['prompt'].progress_apply(get_embedding)


df.to_csv(output_path, index=False)
print(f"\nSaved embeddings to {output_path}")
print(f"Total rows processed: {len(df)}")
print(f"Rows with successful embeddings: {df['embeddings'].notna().sum()}")