from pathlib import Path

from pandas import DataFrame

from src.domain.contracts.loader import BaseLoader


class CSVLoader(BaseLoader):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self, df: DataFrame, chunk_size: int | None = None) -> None:
        output_path = Path(self.file_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"Saved {len(df)} rows into '{output_path}'")
