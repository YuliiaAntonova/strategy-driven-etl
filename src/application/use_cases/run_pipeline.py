from src.domain.contracts.extractor import BaseExtractor
from src.domain.contracts.loader import BaseLoader
from src.domain.contracts.transformer import BaseTransformer


def run_pipeline(
    extractor: BaseExtractor,
    transformer: BaseTransformer,
    loader: BaseLoader,
) -> None:
    df = extractor.extract()
    if df is None:
        raise ValueError("Extractor returned None")
    if df.empty:
        raise ValueError("Extractor returned an empty DataFrame")

    transformed_df = transformer.transform(df)
    if transformed_df.empty:
        raise ValueError("Transformer returned an empty DataFrame")

    loader.load(transformed_df)
