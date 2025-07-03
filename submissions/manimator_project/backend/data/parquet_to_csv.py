import pandas as pd
import os

def parquet_to_csv_simple(parquet_file_path, csv_file_path):
    """
    Converts a Parquet file to a CSV file using Pandas.

    Args:
        parquet_file_path (str): Path to the input Parquet file.
        csv_file_path (str): Path to the output CSV file.
    """
    try:
        print(f"Reading Parquet file: {parquet_file_path}...")
        df = pd.read_parquet(parquet_file_path)

        # Ensure output directory exists
        output_dir = os.path.dirname(csv_file_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created directory: {output_dir}")

        print(f"Writing to CSV file: {csv_file_path}...")
        # index=False is important to avoid writing the DataFrame index as a column
        df.to_csv(csv_file_path, index=False, encoding='utf-8')
        print("Conversion successful!")

    except FileNotFoundError:
        print(f"Error: Parquet file not found at {parquet_file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

# --- Example Usage ---
if __name__ == "__main__":
    input_parquet = "manim_dataset.parquet"
    output_csv_simple = "manim_dataset.csv"

    parquet_to_csv_simple(input_parquet, output_csv_simple)

    