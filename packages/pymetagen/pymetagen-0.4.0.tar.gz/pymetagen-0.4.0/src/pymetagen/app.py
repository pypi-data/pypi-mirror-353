"""
Metagen CLI application.
========================
This module contains the CLI application for the metagen package.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from pprint import pprint

import click

from pymetagen import MetaGen, __version__
from pymetagen.datatypes import (
    MetaGenSupportedFileExtension,
    MetaGenSupportedLoadingMode,
)
from pymetagen.utils import InspectionMode, map_string_to_list_inspection_modes


@click.group(
    "metagen", context_settings={"help_option_names": ["-h", "--help"]}
)
@click.version_option(version=__version__, prog_name="metagen")
def cli():
    """A tool to generate metadata tabular data with the ability to inspect
    data."""


@click.command(
    "metadata", context_settings={"help_option_names": ["-h", "--help"]}
)
@click.version_option(version=__version__, prog_name="metagen")
@click.option(
    "-i",
    "--input",
    type=click.Path(
        file_okay=True,
        dir_okay=True,
        path_type=Path,
        readable=True,
    ),
    required=True,
    help="Input file path. Can be of type: .csv, .parquet, .xlsx, .json",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(
        file_okay=True, dir_okay=False, path_type=Path, writable=True
    ),
    default=None,
    help="Output file path. Can be of type: .csv, .parquet, .xlsx, .json",
)
@click.option(
    "-d",
    "--descriptions",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        path_type=Path,
        readable=True,
    ),
    required=False,
    help=(
        "(optional) Path to a JSON file containing descriptions for each"
        " column."
    ),
)
@click.option(
    "-m",
    "--loading-mode",
    type=click.Choice(["lazy", "eager"], case_sensitive=False),
    callback=lambda ctx, param, value: value.lower(),
    default="lazy",
    required=False,
    help="(optional) Whether to use lazy or eager mode. Defaults to lazy.",
)
@click.option(
    "-xfmt",
    "--extra-formats",
    type=click.STRING,
    required=False,
    default=None,
    help=(
        "Output file formats. Can be of type: .csv, .parquet, .xlsx, .json or "
        "combinations of them, separated by commas, e.g '.csv,.parquet,.json'."
    ),
)
@click.option(
    "-show-desc",
    "--show-descriptions",
    type=click.BOOL,
    default=False,
    is_flag=True,
    help=(
        "(optional flag) Show columns descriptions printed in the console. "
        "Can be of type: True or False. Defaults to False."
    ),
)
@click.option(
    "-P",
    "--preview",
    type=click.BOOL,
    default=False,
    is_flag=True,
    help=(
        "(optional flag) Opens a Quick Look Preview mode of the file. NOTE:"
        " Only works for OS operating systems). Defaults to False."
    ),
)
@click.option(
    "-warn-desc",
    "--warning-description",
    type=click.BOOL,
    default=False,
    is_flag=True,
    help=("(optional flag) in force descriptions for all columns."),
)
def metadata(
    input: Path,
    output: Path | None,
    descriptions: Path | None,
    loading_mode: MetaGenSupportedLoadingMode,
    extra_formats: str | None,
    show_descriptions: bool,
    preview: bool,
    warning_description: bool,
) -> None:
    """
    A tool to generate metadata for tabular data.
    """
    click.echo(f"Generating metadata for {input}...")
    metagen = MetaGen.from_path(
        path=input,
        descriptions_path=descriptions,
        loading_mode=loading_mode,
        compute_metadata=True,
    )
    metadata_by_output_format = metagen.metadata_by_output_format()
    if preview:
        click.echo(f"Opening Quick Look Preview for file: {input}")
        with tempfile.TemporaryDirectory() as tmpdirname:
            output = Path(tmpdirname) / f"{input.stem}-extract.csv"
            metagen.write_metadata(outpath=output)
            metagen.quick_look_preview(output)
    elif output is None:
        click.echo("Metadata:")
        metagen.inspect_data(
            data=metagen._polars_metadata,
            tbl_cols=200,
            tbl_rows=200,
        )
    elif extra_formats:
        splitted_formats = extra_formats.split(",")
        if output.suffix not in splitted_formats:
            splitted_formats.append(output.suffix)
        for output_format in splitted_formats:
            outpath = output.with_suffix(output_format)
            metagen.write_metadata(
                outpath=outpath,
                metadata=metadata_by_output_format[output_format],
            )
    else:
        metagen.write_metadata(outpath=output)

    if show_descriptions:
        click.echo("Column descriptions:")
        pprint(
            metagen._metadata[["Name", "Description"]]
            .set_index("Name")
            .to_dict()["Description"]
        )
    if warning_description:
        message = (
            "Columns without descriptions: "
            f"{metagen._metadata[metagen._metadata['Description'] == '']['Name'].to_list()}"
            "Please add descriptions"
        )
        raise click.ClickException(message=message)


@click.command(
    "inspect", context_settings={"help_option_names": ["-h", "--help"]}
)
@click.option(
    "-i",
    "--input",
    type=click.Path(
        file_okay=True,
        dir_okay=True,
        path_type=Path,
        readable=True,
    ),
    required=True,
    help="Input file path. Can be of type: .csv, .parquet, .xlsx, .json",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(
        file_okay=True, dir_okay=False, path_type=Path, writable=True
    ),
    required=False,
    default=None,
    help="Output file path. Can be of type: .csv, .parquet, .xlsx, .json",
)
@click.option(
    "-m",
    "--loading-mode",
    type=click.Choice(["lazy", "eager"], case_sensitive=False),
    callback=lambda ctx, param, value: value.lower(),
    default="lazy",
    required=False,
    help="(optional) Whether to use lazy or eager mode. Defaults to lazy.",
)
@click.option(
    "-n",
    "--number-rows",
    type=click.INT,
    default=10,
    help="(optional) Maximum number of rows to show. Defaults to 10.",
)
@click.option(
    "-P",
    "--preview",
    type=click.BOOL,
    default=False,
    is_flag=True,
    help=(
        "(optional flag) Opens a Quick Look Preview mode of the file. NOTE:"
        " Only works for OS operating systems). Defaults to False."
    ),
)
@click.option(
    "--fmt-str-lengths",
    type=click.INT,
    default=50,
    help=(
        "(optional) Maximum number of characters for string in a column."
        " Defaults to 50."
    ),
)
@click.option(
    "-im",
    "--inspection-mode",
    type=click.Choice(["head", "tail", "sample"], case_sensitive=True),
    callback=lambda ctx, param, value: value.lower(),
    default="head",
    required=False,
    help=(
        "(optional) Whether to use head, tail or a random sample inspection"
        " mode. Defaults to head."
    ),
)
@click.option(
    "--random-seed",
    type=click.INT,
    default=None,
    required=False,
    help=(
        "(optional) Seed for the random number generator when the sample"
        " inspect mode option is activated. Defaults to None."
    ),
)
@click.option(
    "-wr",
    "--with-replacement",
    type=click.BOOL,
    default=False,
    is_flag=True,
    required=False,
    help=(
        "(optional flag) Allow values to be sampled more than once when the"
        " sample inspect mode option is activated. Defaults to False."
    ),
)
def inspect(
    input: Path,
    output: Path | None,
    loading_mode: MetaGenSupportedLoadingMode,
    number_rows: int,
    preview: bool,
    fmt_str_lengths: int,
    inspection_mode: InspectionMode,
    random_seed: int,
    with_replacement: bool,
) -> None:
    """
    A tool to inspect a data set.
    """
    metagen = MetaGen.from_path(path=input, loading_mode=loading_mode)
    columns_length = metagen.columns_length
    metagen.extract_data(
        tbl_rows=number_rows,
        inspection_mode=inspection_mode,
        random_seed=random_seed,
        with_replacement=with_replacement,
        inplace=True,
    )
    if output:
        click.echo(f"Writing extract in: {output}")
        metagen.write_data(outpath=output)
    elif preview:
        click.echo(f"Opening Quick Look Preview for file: {input}")
        with tempfile.TemporaryDirectory() as tmpdirname:
            output = Path(tmpdirname) / f"{input.stem}-extract.csv"
            metagen.write_data(outpath=output)
            metagen.quick_look_preview(output)
    else:
        click.echo(f"Inspecting file {input}:")
        metagen.inspect_data(
            tbl_rows=number_rows,
            tbl_cols=columns_length,
            fmt_str_lengths=fmt_str_lengths,
        )


@click.command(
    "extracts", context_settings={"help_option_names": ["-h", "--help"]}
)
@click.option(
    "-i",
    "--input",
    type=click.Path(
        file_okay=True,
        dir_okay=True,
        path_type=Path,
        readable=True,
    ),
    required=True,
    help="Input file path. Can be of type: .csv, .parquet, .xlsx, .json",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(
        file_okay=True, dir_okay=False, path_type=Path, writable=True
    ),
    required=True,
    default=None,
    help="Output file path. Can be of type: .csv, .parquet, .xlsx, .json",
)
@click.option(
    "-m",
    "--loading-mode",
    type=click.Choice(["lazy", "eager"], case_sensitive=False),
    callback=lambda ctx, param, value: value.lower(),
    default="lazy",
    required=False,
    help="(optional) Whether to use lazy or eager mode. Defaults to lazy.",
)
@click.option(
    "-n",
    "--number-rows",
    type=click.INT,
    default=10,
    help="(optional) Maximum number of rows to show. Defaults to 10.",
)
@click.option(
    "--random-seed",
    type=click.INT,
    default=None,
    required=False,
    help=(
        "(optional) Seed for the random number generator when the sample"
        " inspect mode option is activated. Defaults to None."
    ),
)
@click.option(
    "-wr",
    "--with-replacement",
    type=click.BOOL,
    default=False,
    is_flag=True,
    required=False,
    help=(
        "(optional flag) Allow values to be sampled more than once when the"
        " sample inspect mode option is activated. Defaults to False."
    ),
)
@click.option(
    "-xfmt",
    "--extra-formats",
    type=click.STRING,
    required=False,
    default=None,
    help=(
        "Output file formats. Can be of type: .csv, .parquet, .xlsx, .json or "
        "combinations of them, separated by commas, e.g '.csv,.parquet,.json'."
    ),
)
@click.option(
    "-ignore-im",
    "--ignore-inspection-modes",
    type=click.STRING,
    required=False,
    help=(
        "Comma-separated list of inspection modes to ignore. Can be of type:"
        " head, tail, sample."
    ),
)
def extracts(
    input: Path,
    output: Path,
    loading_mode: MetaGenSupportedLoadingMode,
    number_rows: int,
    random_seed: int,
    with_replacement: bool,
    extra_formats: str | None,
    ignore_inspection_modes: str | None,
) -> None:
    """
    A tool to extract n number of rows from a data set. It can extract
    head, tail, random sample at the same time.
    """
    metagen = MetaGen.from_path(path=input, loading_mode=loading_mode)
    inspection_modes = map_string_to_list_inspection_modes(
        ignore_inspection_modes
    )
    formats_to_write = {
        MetaGenSupportedFileExtension.writable_extension(output.suffix)
    }
    if extra_formats:
        extra_format_enums = set(
            map(
                MetaGenSupportedFileExtension.writable_extension,
                extra_formats.replace(" ", "").split(","),
            )
        )
        formats_to_write = formats_to_write & extra_format_enums
    click.echo("Writing extracts...")
    metagen.write_extracts(
        output_path=output,
        number_rows=number_rows,
        random_seed=random_seed,
        with_replacement=with_replacement,
        inspection_modes=inspection_modes,
        formats_to_write=formats_to_write,
    )


@click.command(
    "filter", context_settings={"help_option_names": ["-h", "--help"]}
)
@click.option(
    "-i",
    "--input",
    type=click.Path(
        file_okay=True,
        dir_okay=True,
        path_type=Path,
        readable=True,
    ),
    required=True,
    help="Input file path. Can be of type: .csv, .parquet, .xlsx, .json",
)
@click.option(
    "-t",
    "--table-name",
    type=click.STRING,
    required=False,
    default=None,
    help="Name of the table to filter. Defaults to the input file name.",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(
        file_okay=True, dir_okay=False, path_type=Path, writable=True
    ),
    required=False,
    help="Output file path. Can be of type: .csv, .parquet, .xlsx, .json",
)
@click.option(
    "-q",
    "--query",
    required=True,
    help="SQL query string/file to apply to the data.",
)
@click.option(
    "-m",
    "--loading-mode",
    type=click.Choice(["lazy", "eager"], case_sensitive=False),
    callback=lambda ctx, param, value: value.lower(),
    default="lazy",
    required=False,
    help="(optional) Whether to use lazy or eager mode. Defaults to lazy.",
)
@click.option(
    "-e",
    "--eager",
    type=click.BOOL,
    default=True,
    help="(optional) Whether to use lazy or eager mode. Defaults to lazy.",
)
@click.option(
    "-P",
    "--preview",
    type=click.BOOL,
    default=False,
    is_flag=True,
    help=(
        "(optional flag) Opens a Quick Look Preview mode of the file. NOTE:"
        " Only works for OS operating systems). Defaults to False."
    ),
)
def filter(
    input: Path,
    table_name: str | None,
    output: Path | None,
    query: str | Path,
    loading_mode: MetaGenSupportedLoadingMode,
    eager: bool,
    preview: bool,
) -> None:
    """
    A tool to filter a data set.
    """
    metagen = MetaGen.from_path(path=input, loading_mode=loading_mode)
    table_name = table_name or input.stem
    metagen.filter_data(table_name, query, eager=eager)
    if output:
        click.echo(f"Writing filtered data in: {output}")
        metagen.write_data(outpath=output)
    elif preview:
        click.echo(f"Opening Quick Look Preview for file: {input}")
        with tempfile.TemporaryDirectory() as tmpdirname:
            stem = input.stem.replace("*", "concatenation")
            output = Path(tmpdirname) / f"{stem}-filtered.csv"
            metagen.write_data(outpath=output)
            metagen.quick_look_preview(output)
    else:
        click.echo("Filtered data:")
        metagen.inspect_data()


cli.add_command(metadata)
cli.add_command(inspect)
cli.add_command(extracts)
cli.add_command(filter)


if __name__ == "__main__":
    cli(auto_envvar_prefix="METAGEN")
