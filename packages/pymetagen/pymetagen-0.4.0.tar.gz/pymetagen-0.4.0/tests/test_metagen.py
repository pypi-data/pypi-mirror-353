from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pandas as pd
import polars as pl
import pytest

from pymetagen import MetaGen, json_metadata_to_pandas
from pymetagen._typing import DataFrameT
from pymetagen.datatypes import (
    MetaGenMetadataColumn,
    MetaGenSupportedLoadingMode,
)
from pymetagen.exceptions import (
    FileTypeUnsupportedError,
    LoadingModeUnsupportedError,
)
from pymetagen.utils import InspectionMode

input_paths = ["input_csv_path", "input_parquet_path", "input_xlsx_path"]


@pytest.mark.parametrize(
    "data",
    [
        "eager_data",
        "lazy_data",
    ],
)
class TestMetaGen:
    """
    Test the MetaGen class on both eager and lazy data.

    Each test is parametrized with the data fixture name and should run:

    ```
    data = request.getfixturevalue(data)
    ```

    to get the data.
    """

    def test_init(self, data: str, request: pytest.FixtureRequest):
        df: DataFrameT = request.getfixturevalue(data)
        MetaGen(
            data=df,
        )

    def test_compute_metadata(self, data: str, request: pytest.FixtureRequest):
        df: DataFrameT = request.getfixturevalue(data)
        metagen = MetaGen(data=df)
        metadata = metagen.compute_metadata()

        assert set(metadata.index) == set(metagen.columns)

    @pytest.mark.parametrize(
        "extension, read_metadata",
        [
            ["csv", lambda x: pd.read_csv(x)],
            [
                "xlsx",
                lambda x: pd.read_excel(x, engine="openpyxl"),
            ],
            ["json", json_metadata_to_pandas],
            ["parquet", pd.read_parquet],
        ],
    )
    def test_write(
        self,
        extension: str,
        data: str,
        tmp_dir_path: Path,
        read_metadata: Callable,
        request: pytest.FixtureRequest,
    ):
        df: DataFrameT = request.getfixturevalue(data)
        outpath = tmp_dir_path / f"out.{extension}"

        metagen = MetaGen(data=df)
        metagen.write_metadata(outpath=outpath)

        assert outpath.exists()
        assert outpath.is_file()
        pd.DataFrame().reset_index()
        outdata = read_metadata(outpath)

        if extension == "json":
            outdata.reset_index(names=["Name"], inplace=True)

        assert len(outdata) == metagen.columns_length
        assert list(
            outdata.columns
        ) == MetaGenMetadataColumn.pymetagen_columns(include_name_column=True)


@pytest.mark.parametrize(
    "df_constructor",
    [
        pl.DataFrame,
        pl.LazyFrame,
    ],
)
class TestMetadataMethods:
    """Run tests on individual methods of the MetaGen class."""

    def test__number_of_unique_counts(
        self, df_constructor: Callable, columns_with_nulls
    ):
        df = df_constructor(columns_with_nulls)

        metagen = MetaGen(data=df)
        n_unique = metagen._number_of_unique_counts()
        assert n_unique == {"all_nulls": 1, "no_nulls": 5, "mixed": 4}

    def test__number_of_unique_values(
        self, df_constructor: Callable, columns_with_nulls
    ):
        df = df_constructor(columns_with_nulls)

        metagen = MetaGen(data=df)
        n_unique = metagen._number_of_unique_values()
        assert n_unique == {
            "all_nulls": [None],
            "no_nulls": [1, 2, 3, 4, 5],
            "mixed": [1, 2, 3, None],
        }

    @pytest.mark.parametrize(
        ["eager", "return_type"],
        [[True, pl.DataFrame], [False, pl.LazyFrame]],
    )
    def test__filter_by_sql_query(
        self, df_constructor: Callable, eager: bool, return_type: DataFrameT
    ):
        df = pl.DataFrame(
            data=list(
                zip(
                    ("The Godfather", 1972, 6_000_000, 134_821_952, 9.2),
                    ("The Dark Knight", 2008, 185_000_000, 533_316_061, 9.0),
                    ("Schindler's List", 1993, 22_000_000, 96_067_179, 8.9),
                    ("Pulp Fiction", 1994, 8_000_000, 107_930_000, 8.9),
                    (
                        "The Shawshank Redemption",
                        1994,
                        25_000_000,
                        28_341_469,
                        9.3,
                    ),
                ),
            ),
            schema=[
                ("title", str),
                ("release_year", int),
                ("budget", int),
                ("gross", int),
                ("imdb_score", float),
            ],
        )

        metagen = MetaGen(data=df)
        filtered = metagen._filter_by_sql_query(
            sql_query="""
            SELECT title, release_year, imdb_score
            FROM data
            WHERE release_year > 1990
            ORDER BY imdb_score DESC
            """,
            eager=eager,
        )
        assert isinstance(filtered, return_type)  # type: ignore


@pytest.mark.parametrize(
    "column_name, expected_value",
    [
        ["# nulls", 5],
        ["# empty/zero", 5],
        ["# unique", 1],
        ["Values", [None]],
    ],
)
def test_metadata_data_frame_with_null_column(
    column_name: str,
    expected_value: int | None,
):
    null_data = {
        "data_values": [None, None, None, None, None],
    }
    null_data_frame = pl.DataFrame(null_data, schema={"data_values": pl.Null})
    metagen = MetaGen(data=null_data_frame)
    metadata_df = metagen.compute_metadata()
    metadata_dict = metadata_df.to_dict(orient="records").pop()

    assert metadata_dict[column_name] == expected_value


@pytest.mark.parametrize(
    "mode",
    MetaGenSupportedLoadingMode.values(),
)
class TestMetaGenFromPath:
    @pytest.mark.parametrize(
        "path",
        input_paths,
    )
    def test_from_path(
        self,
        path: str,
        mode: MetaGenSupportedLoadingMode,
        request: pytest.FixtureRequest,
    ):
        file_path: Path = request.getfixturevalue(path)
        MetaGen.from_path(
            path=file_path,
            loading_mode=mode,
        )

    def test_unsupported_path(
        self,
        tmp_dir_path: Path,
        mode: MetaGenSupportedLoadingMode,
    ):
        with pytest.raises(FileTypeUnsupportedError):
            MetaGen.from_path(
                path=tmp_dir_path / "test.unsupported",
                loading_mode=mode,
            )

    @pytest.mark.parametrize(
        "descriptions_path",
        [
            "descriptions_csv_path",
            "descriptions_json_path",
        ],
    )
    def test_with_descriptions(
        self,
        descriptions_path: str,
        request: pytest.FixtureRequest,
        input_csv_path: Path,
        mode: MetaGenSupportedLoadingMode,
    ):
        description_path: Path = request.getfixturevalue(descriptions_path)

        metagen = MetaGen.from_path(
            path=input_csv_path,
            descriptions_path=description_path,
            loading_mode=mode,
        )
        metadata = metagen.compute_metadata()

        for field in ["Description", "Long Name"]:
            assert field in metadata.columns
            assert metadata[field].notnull().all()
            assert metadata[field].notna().all()


def test_from_path_unsupported_mode(tmp_dir_path: Path):
    with pytest.raises(LoadingModeUnsupportedError):
        MetaGen.from_path(
            path=tmp_dir_path / "test.csv",
            loading_mode="unsupported_mode",  # type: ignore
        )


def test_write_metadata_unsupported_extension(tmp_dir_path: Path):
    metagen = MetaGen(data=pl.DataFrame())
    with pytest.raises(FileTypeUnsupportedError):
        metagen.write_metadata(tmp_dir_path / "test.unsupported")


def test_load_file_extension_none(
    tmp_dir_path: Path,
):
    with pytest.raises(FileTypeUnsupportedError):
        MetaGen.from_path(
            path=tmp_dir_path / "test",
            loading_mode=MetaGenSupportedLoadingMode.LAZY,
        )


def test_file_extension_none_for_parquet_directories(test_data_dir: Path):
    path = test_data_dir / "input_ab_partition"
    MetaGen.from_path(
        path=path,
        loading_mode=MetaGenSupportedLoadingMode.LAZY,
    )


def test_file_extension_none_for_directories_with_no_parquet_files(
    test_data_dir: Path,
):
    path = test_data_dir / "directory_without_parquet"
    with pytest.raises(FileTypeUnsupportedError):
        MetaGen.from_path(
            path=path,
            loading_mode=MetaGenSupportedLoadingMode.LAZY,
        )


class TestMetaGenExtractData:
    """Test extract data functionality."""

    @pytest.mark.parametrize(
        "inspection_mode",
        InspectionMode.list(),
    )
    @pytest.mark.parametrize(
        "mode",
        MetaGenSupportedLoadingMode.list(),
    )
    def test_extract_data_inspect_mode(
        self,
        mode: MetaGenSupportedLoadingMode,
        inspection_mode: InspectionMode,
        test_data_dir: Path,
    ):
        metagen = MetaGen.from_path(
            test_data_dir / "input_ab_partition.parquet", loading_mode=mode
        )

        extract = metagen.extract_data(
            tbl_rows=2, inspection_mode=inspection_mode
        )

        assert extract.shape[0] == 2
        assert isinstance(extract, pl.DataFrame)


class TestMetaGenWriteExtracts:

    @pytest.mark.parametrize(
        "mode",
        MetaGenSupportedLoadingMode.list(),
    )
    @pytest.mark.parametrize(
        "inspection_mode",
        InspectionMode.list(),
    )
    def test_write_extract_by_inspection_mode(
        self,
        tmp_dir_path,
        inspection_mode: InspectionMode,
        mode: MetaGenSupportedLoadingMode,
        test_data_dir: Path,
    ):
        metagen = MetaGen.from_path(
            path=test_data_dir / "input_ab_partition.parquet",
            loading_mode=mode,
        )
        file_name = f"test-{inspection_mode}.csv"
        metagen.write_extract_by_inspection_mode(
            output_path=tmp_dir_path / file_name,
            inspection_mode=inspection_mode,
            random_seed=None,
            number_rows=2,
            with_replacement=False,
        )

        assert (tmp_dir_path / file_name).exists()
        assert (tmp_dir_path / file_name).is_file()

    @pytest.mark.parametrize(
        "mode",
        MetaGenSupportedLoadingMode.list(),
    )
    def test_write_extracts(
        self,
        tmp_dir_path: Path,
        mode: MetaGenSupportedLoadingMode,
        test_data_dir: Path,
    ):
        metagen = MetaGen.from_path(
            path=test_data_dir / "input_ab_partition.parquet",
            loading_mode=mode,
        )
        metagen.write_extracts(
            output_path=tmp_dir_path / "test.csv", number_rows=2
        )
        for inspection_mode in InspectionMode.values():
            file_name = f"test-{inspection_mode}.csv"
            assert (tmp_dir_path / file_name).exists()
            assert (tmp_dir_path / file_name).is_file()
            assert (tmp_dir_path / file_name).stat().st_size > 0
