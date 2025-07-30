"""
Data Loader
===========
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any

import polars as pl
from polars.datatypes.constants import N_INFER_DEFAULT

from pymetagen._typing import DataFrameT
from pymetagen.datatypes import MetaGenSupportedFileExtension
from pymetagen.exceptions import FileTypeUnsupportedError
from pymetagen.utils import get_nested_path, selectively_update_dict

POLARS_DEFAULT_READ_CSV_OPTIONS: dict[str, Any] = {
    "columns": None,
    "use_pyarrow": False,
    "n_rows": None,
    "row_index_name": None,
    "row_index_offset": 0,
    "low_memory": False,
    "rechunk": True,
    "has_header": True,
    "new_columns": None,
    "separator": ",",
    "comment_prefix": None,
    "quote_char": r'"',
    "skip_rows": 0,
    "schema_overrides": None,
    "null_values": None,
    "missing_utf8_is_empty_string": False,
    "ignore_errors": False,
    "try_parse_dates": False,
    "n_threads": None,
    "infer_schema_length": N_INFER_DEFAULT,
    "batch_size": 8192,
    "encoding": "utf8",
    "storage_options": None,
    "skip_rows_after_header": 0,
    "sample_size": 1024,
    "eol_char": "\n",
    "raise_if_empty": True,
}

POLARS_DEFAULT_LAZY_READ_CSV_OPTIONS: dict[str, Any] = (
    POLARS_DEFAULT_READ_CSV_OPTIONS.copy()
)
lazy_csv_unsupported_options = [
    "columns",
    "use_pyarrow",
    "n_threads",
    "batch_size",
    "storage_options",
    "sample_size",
]
for option in lazy_csv_unsupported_options:
    del POLARS_DEFAULT_LAZY_READ_CSV_OPTIONS[option]

LIST_OF_EXCEL_OPTIONS_FROM_CSV_OPTIONS: list[Any] = []
POLARS_DEFAULT_READ_EXCEL_OPTIONS: dict[str, Any] = {
    key: value
    for key, value in POLARS_DEFAULT_READ_CSV_OPTIONS.items()
    if key in LIST_OF_EXCEL_OPTIONS_FROM_CSV_OPTIONS
}
POLARS_DEFAULT_READ_EXCEL_OPTIONS["engine"] = "openpyxl"


POLARS_DEFAULT_READ_PARQUET_OPTIONS: dict[str, Any] = {}


class DataLoader:
    def __init__(
        self,
        path: Path | str,
        polars_read_csv_options: None | dict[str, Any] = None,
        sheet_name: str | None = None,
        _default_read_csv_options: dict[
            str, Any
        ] = POLARS_DEFAULT_READ_CSV_OPTIONS,
        _default_read_excel_options: dict[
            str, Any
        ] = POLARS_DEFAULT_READ_EXCEL_OPTIONS,
        _default_read_parquet_options: dict[
            str, Any
        ] = POLARS_DEFAULT_READ_PARQUET_OPTIONS,
    ):
        self.path = Path(path)
        self.polars_read_csv_options = _default_read_csv_options.copy()
        self._update_read_csv_polars_options(polars_read_csv_options)
        self.polars_read_excel_options: dict[str, Any] = (
            _default_read_excel_options.copy()
        )
        self._update_polars_read_excel_options(sheet_name)
        self.polars_read_parquet_options = _default_read_parquet_options.copy()

    def __call__(self):
        return self.load()

    def load(
        self,
    ) -> DataFrameT:
        extension_mapping = {
            MetaGenSupportedFileExtension.CSV: self._load_csv_data,
            MetaGenSupportedFileExtension.XLSX: self._load_excel_data,
            MetaGenSupportedFileExtension.PARQUET: self._load_parquet_data,
            MetaGenSupportedFileExtension.JSON: self._load_json_data,
            MetaGenSupportedFileExtension.NONE: self._load_none_suffix,
        }
        try:
            file_extension = MetaGenSupportedFileExtension(self.path.suffix)
        except ValueError:
            raise FileTypeUnsupportedError(
                f"File extension for {self.path} is not supported"
            )
        return extension_mapping[file_extension]()

    def _update_polars_read_excel_options(
        self,
        sheet_name: str | None,
    ) -> dict[str, Any]:
        self.polars_read_excel_options["sheet_name"] = sheet_name
        return self.polars_read_excel_options

    def _update_read_csv_polars_options(
        self, polars_read_csv_options: dict[str, Any] | None
    ) -> None:
        if polars_read_csv_options is None:
            return
        self.polars_read_csv_options = selectively_update_dict(
            self.polars_read_csv_options, polars_read_csv_options
        )

    def _load_csv_data(self) -> DataFrameT:
        return pl.read_csv(source=self.path, **self.polars_read_csv_options)

    def _load_excel_data(self) -> pl.DataFrame:
        return pl.read_excel(
            source=self.path, **self.polars_read_excel_options
        )

    def _load_parquet_data(self) -> DataFrameT:
        """
        IMPORTANT:
        reading the same data of partitioned parquet files with different
        partitions will not preserve the column order. This is a limitation of
        polars.
        """
        pl.enable_string_cache()
        path = get_nested_path(self.path)
        return pl.read_parquet(
            source=path,
            hive_partitioning=True,
            **self.polars_read_parquet_options,
        )

    def _load_json_data(self):
        raise NotImplementedError

    def _load_none_suffix(self):
        """
        Only used for partitioned parquet files that have no suffix.
        """
        if not self.path.is_dir():
            raise FileTypeUnsupportedError(
                f"File {self.path} is not a directory"
            )

        if ".parquet" not in get_nested_path(self.path):
            raise FileTypeUnsupportedError(
                f"Directory {self.path} does not contain any parquet files"
            )

        return self._load_parquet_data()


class LazyDataLoader(DataLoader):
    def __init__(
        self,
        path: Path | str,
        polars_read_csv_options: None | dict[str, Any] = None,
        sheet_name: str | None = None,
    ):
        super().__init__(
            path=path,
            polars_read_csv_options=polars_read_csv_options,
            sheet_name=sheet_name,
            _default_read_csv_options=POLARS_DEFAULT_LAZY_READ_CSV_OPTIONS,
        )

    def load(self) -> DataFrameT:
        return super().load()

    def _load_csv_data(self) -> pl.LazyFrame:
        return pl.scan_csv(source=self.path, **self.polars_read_csv_options)

    def _load_excel_data(self) -> pl.DataFrame:
        warnings.warn(
            "Excel files are not supported in lazy mode, switching to full"
            " mode"
        )
        return super()._load_excel_data()

    def _load_parquet_data(self) -> pl.LazyFrame:
        pl.enable_string_cache()
        path = get_nested_path(self.path)
        return pl.scan_parquet(
            source=path,
            hive_partitioning=True,
            **self.polars_read_parquet_options,
        )
