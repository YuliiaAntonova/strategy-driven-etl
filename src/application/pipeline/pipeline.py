from __future__ import annotations

from collections.abc import Callable, Iterable

from pandas import DataFrame

from src.domain.contracts.change_detector import BaseChangeDetector
from src.domain.contracts.extractor import BaseExtractor
from src.domain.contracts.transformer import BaseTransformer
from src.domain.contracts.write_strategy import BaseWriteStrategy


class Pipeline:
    def __init__(
        self,
        extractor: BaseExtractor,
        transformer: BaseTransformer,
        change_detector: BaseChangeDetector,
        state_reader: Callable[[], DataFrame],
        writer_resolver: Callable[[int], BaseWriteStrategy],
        write_chunk_size: int | None = None,
    ):
        self.extractor = extractor
        self.transformer = transformer
        self.change_detector = change_detector
        self.state_reader = state_reader
        self.writer_resolver = writer_resolver
        self.write_chunk_size = write_chunk_size

    def run(self, extract_chunk_size: int | None = None) -> None:
        any_rows_written = False

        total_processed = 0
        total_written = 0

        for batch_index, batch_df in enumerate(self._iter_batches(extract_chunk_size)):
            batch_count = len(batch_df)
            total_processed += batch_count

            print(f"Processing batch {batch_index}: {batch_count} rows")

            transformed_df = self.transformer.transform(batch_df)
            existing_df = self.state_reader()
            changes = self.change_detector.detect(transformed_df, existing_df)

            if changes.has_writes:
                any_rows_written = True

                written_count = len(changes.to_insert) if hasattr(changes, "to_insert") else batch_count
                total_written += written_count

                writer = self.writer_resolver(batch_index)
                writer.write(changes, chunk_size=self.write_chunk_size)

        if any_rows_written:
            print(f"Finished pipeline: processed={total_processed}, written={total_written}")
        else:
            print(f"Finished pipeline: processed={total_processed}, written=0")
            print("No data to load")

    def _iter_batches(self, extract_chunk_size):
        if extract_chunk_size and hasattr(self.extractor, "extract_in_chunks"):
            print(f"Using chunked extraction: chunk_size={extract_chunk_size}")
            return self.extractor.extract_in_chunks(extract_chunk_size)

        print("Using full extraction")
        return [self.extractor.extract()]
