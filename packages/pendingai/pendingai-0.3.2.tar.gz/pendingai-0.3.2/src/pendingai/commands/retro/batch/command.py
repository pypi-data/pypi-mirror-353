#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from __future__ import annotations

import json
import os
import pathlib
import typing

import rich
import rich.progress
import rich.prompt
import rich.table
import typer

from pendingai import config
from pendingai.commands.retro.batch.controller import RetroBatchController
from pendingai.commands.retro.batch.models import (
    Batch,
    BatchJobResult,
    BatchPage,
    BatchStatus,
)
from pendingai.commands.retro.controller import RetroController
from pendingai.context import Context
from pendingai.utils import formatters, regex_patterns

console = rich.console.Console(theme=config.RICH_CONSOLE_THEME, soft_wrap=True)

app = typer.Typer(
    name="batch",
    help=(
        "Batch operations enabling high-throughput, large-scale "
        "campaigns to assess molecule synthesizability."
    ),
    short_help="Batched operations for high-throughput synthesizability assessment.",
    no_args_is_help=True,
    add_completion=False,
    pretty_exceptions_show_locals=False,
    rich_markup_mode=None,
    context_settings={"max_content_width": config.CONSOLE_WIDTH},
)

# region callbacks -----------------------------------------------------


def engine_callback(context: Context, engine: str | None) -> str:
    """
    Check an optional retrosynthesis engine id is available and exists
    in the database; if not provided then select a default engine or the
    latest alive engine.

    Args:
        context (Context): App runtime context.
        engine (str, optional): Retrosynthesis engine id.

    Raises:
        typer.BadParameter: Retrosynthesis engine id does not exist or
            is not currently available.

    Returns:
        str: Retrosynthesis engine id.
    """
    items: list = RetroController(context).retrieve_retrosynthesis_engines()
    items.sort(key=lambda x: x.last_alive, reverse=True)
    items.sort(key=lambda x: x.default, reverse=True)
    if engine:
        if len(engine) < 11:
            raise typer.BadParameter("Retrosynthesis engine not available.")
        matches: list[str] = [x for x in [x.id for x in items] if x.startswith(engine)]
        if len(matches) == 0:
            raise typer.BadParameter("Retrosynthesis engine not available.")
        elif len(matches) > 1:
            raise typer.BadParameter("ID matches more than 1 engine, use a longer ID.")
        engine = matches[0]
    elif len(items) == 0:
        raise typer.BadParameter("No retrosynthesis engine is available.")
    elif engine is None:
        engine = items[0].id
    return engine


def libraries_callback(context: Context, libraries: list[str] | None) -> list[str]:
    """
    Check an optional collection of building block libraries are
    available and exist in the database; if none exist then select all
    libraries that are currently available.

    Args:
        context (Context): App runtime context.
        libraries (list[str], optional): Building block library ids.

    Raises:
        typer.BadParameter: Building block library ids do not exist; if
            at least one is not found.

    Returns:
        list[str]: Building block library ids.
    """
    items: list = RetroController(context).retrieve_building_block_libraries()
    if len(items) == 0:
        raise typer.BadParameter("No building block library is available.")
    elif not libraries:
        libraries = [x.id for x in items]
    else:
        for library in libraries:
            if library not in [x.id for x in items]:
                raise typer.BadParameter(f"Building block library not found: {library}.")
    return libraries


def page_size_callback(page_size: int | None) -> int | None:
    """
    Page size options require an enumeration, to avoid this we do a
    quick lookup in the range [5, 25] with step size 5 to check it is a
    valid interval value.

    Args:
        page_size (int, optional): Page size option.

    Raises:
        typer.BadParameter: Page size value is not a valid interval.

    Returns:
        int: Page size option.
    """
    if page_size and page_size not in range(5, 26, 5):
        raise typer.BadParameter("Must be an interval of 5.")
    return page_size


def validate_input_file_upload_size(input_file: pathlib.Path) -> pathlib.Path:
    """
    Check file size of an input file being uploaded, used to prevent an
    oversized payload from exceeding the quote limit for the api layer.

    Args:
        input_file (pathlib.Path): Input filepath.

    Raises:
        typer.BadParameter: File exceeds upload size limit.

    Returns:
        pathlib.Path: Input filepath.
    """
    # check filesize upload limit is not exceeded by the input file
    # argument and raise appropriately if it does.
    if input_file and os.path.getsize(input_file) > config.FILE_SIZE_UPLOAD_LIMIT:
        upload_limit: float = config.FILE_SIZE_UPLOAD_LIMIT / 1e6
        raise typer.BadParameter(f"Exceeded size limit of {upload_limit:.1f}MB.")
    return input_file


def batch_id_callback(context: Context, batch_id: str | None) -> str | None:
    """
    Validate a batch id parameter by checking it follows a required
    regex pattern and then requesting the batch resource from the api
    layer to confirm it exists.

    Args:
        context (Context): App runtime context.
        batch_id (str, optional): Batch resource id.

    Raises:
        typer.BadParameter: Batch does not exist.

    Returns:
        str: Batch resource id.
    """
    if batch_id:
        controller = RetroBatchController(context)
        is_invalid: bool = regex_patterns.BATCH_ID_PATTERN.match(batch_id) is None
        if is_invalid or not controller.check_batch_exists(batch_id):
            raise typer.BadParameter("Batch does not exist.")
    return batch_id


# region command: submit -----------------------------------------------


@app.command(
    "submit",
    help=(
        "Submit multiple retrosynthesis jobs together as a single batch. "
        "All jobs in the batch will share the same job parameters."
    ),
    short_help="Submit a batch of retrosynthesis jobs.",
)
def _create(
    context: Context,
    input_file: typing.Annotated[
        pathlib.Path,
        typer.Argument(
            metavar="SMILES_FILE",
            help=(
                "Input file with one molecule SMILES per line. "
                "Repeated SMILES will be removed automatically."
            ),
            callback=validate_input_file_upload_size,
            resolve_path=True,
            file_okay=True,
            dir_okay=False,
            exists=True,
        ),
    ],
    retrosynthesis_engine: typing.Annotated[
        str | None,
        typer.Option(
            "--engine",
            help="Retrosynthesis engine id. Defaults to primary engine.",
            callback=engine_callback,
        ),
    ] = None,
    building_block_libraries: typing.Annotated[
        list[str] | None,
        typer.Option(
            "--library",
            help="Building block library ids. Defaults to all available libraries.",
            callback=libraries_callback,
        ),
    ] = None,
    number_of_routes: typing.Annotated[
        int,
        typer.Option(
            "--num-routes",
            help="Maximum number of retrosynthetic routes to generate. Defaults to 20.",
            show_default=False,
            metavar="INTEGER",
            min=1,
            max=50,
        ),
    ] = 20,
    processing_time: typing.Annotated[
        int,
        typer.Option(
            "--time-limit",
            help="Maximum processing time in seconds. Defaults to 300.",
            show_default=False,
            metavar="INTEGER",
            min=60,
            max=600,
        ),
    ] = 300,
    reaction_limit: typing.Annotated[
        int,
        typer.Option(
            "--reaction-limit",
            help=(
                "Maximum number of times a specific reaction can "
                "appear in generated retrosynthetic routes. Defaults "
                "to 3."
            ),
            show_default=False,
            metavar="INTEGER",
            min=1,
            max=20,
        ),
    ] = 3,
    building_block_limit: typing.Annotated[
        int,
        typer.Option(
            "--block-limit",
            help=(
                "Maximum number of times a building block can appear "
                "in a single retrosynthetic route. Default to 3."
            ),
            show_default=False,
            metavar="INTEGER",
            min=1,
            max=20,
        ),
    ] = 3,
) -> str:
    """
    Submit a batch of retrosynthesis jobs for a given input file with
    line-delimited smiles; validate request input file data and send a
    batch submission request.

    Args:
        context (Context): App runtime context.
        input_file (pathlib.Path): Filepath containing line-delimited
            molecule smiles mapping to individual jobs.
        retrosynthesis_engine (str, optional): Retrosynthesis engine
            id. Defaults to primary engine.
        building_block_libraries (list[str], optional): Building block
            library ids. Defaults to all available libraries.
        number_of_routes (int, optional): Maximum number of
            retrosynthetic routes to generate. Defaults to 20.
        processing_time (int, optional): Maximum processing time in
            seconds. Defaults to 300.
        reaction_limit (int, optional): Maximum number of times a
            specific reaction can appear in generated retrosynthetic
            routes. Defaults to 3.
        building_block_limit (int, optional): Maximum number of times a
            building block can appear in a single retrosynthetic route.
            Default to 3.

    Raises:
        typer.BadParameter: An input molecule has invalid regex pattern.
        typer.BadParameter: File contains no valid SMILES strings.
        typer.BadParameter: File contains non-UTF-8 encodable characters.

    Returns:
        str: Batch resource id.
    """
    controller = RetroBatchController(context)

    # iterate over the input file and validate each line as a mol smiles
    # and error on invalid smiles pointing to a line number.
    valid_smiles_count = 0
    desc: str = f"Parsing molecules from input file: {input_file}"
    opts: dict = {"pulse_style": None, "transient": True}
    smiles_set: set[str] = set()

    try:
        with rich.progress.open(input_file, "rb", description=desc, **opts) as file:
            for line_no, line in enumerate(file, start=1):
                try:
                    smiles: str = line.decode("utf-8").strip()
                except UnicodeDecodeError:
                    unicode_decode_err_msg: str = (
                        f"Non-UTF-8 character detected at line {line_no}. "
                        f"Please ensure file uses UTF-8 encoding."
                    )
                    raise typer.BadParameter(
                        unicode_decode_err_msg, param_hint="SMILES_FILE"
                    )

                if not smiles or smiles == "":  # Skip empty lines
                    continue

                if regex_patterns.SMILES_PATTERN.match(smiles) is None:
                    smiles_pattern_err_msg: str = (
                        f"Molecule SMILES is invalid '{smiles}' (line {line_no})."
                    )
                    raise typer.BadParameter(
                        smiles_pattern_err_msg, param_hint="SMILES_FILE"
                    )

                valid_smiles_count += 1
                smiles_set.add(smiles)

                if len(smiles_set) > 100_000:
                    raise typer.BadParameter(
                        "Batches are limited to a maximum size of 100,000.",
                        param_hint="SMILES_FILE",
                    )

    except IOError as e:
        raise typer.BadParameter(
            f"Error reading input file: {str(e)}", param_hint="SMILES_FILE"
        )

    # Check if file had any valid SMILES
    if valid_smiles_count == 0:
        raise typer.BadParameter(
            "Input file contains no valid SMILES strings.", param_hint="SMILES_FILE"
        )

    console.print(
        f"[warn][not b]! Found {valid_smiles_count} valid job(s) from input file."
    )

    filename: str = formatters.format_filename(input_file.name)
    console.print(f"[warn]! Storing a sanitized filename: {filename}")

    batch: Batch = controller.create_batch(
        list(smiles_set),
        input_file,
        retrosynthesis_engine,  # type: ignore
        building_block_libraries,  # type: ignore
        number_of_routes,
        processing_time,
        reaction_limit,
        building_block_limit,
        filename,
    )

    # report outcome from the submit; show the batch id and the number
    # of unique submitted molecules.
    console.print(f"[success]✓ Batch submitted successfully with id: {batch.id}")
    console.print(f"[success]- Number of newly created jobs: {len(smiles_set)}")
    return batch.id


# region command: status -----------------------------------------------


@app.command(
    "status",
    help=(
        "Check the overall status of a retrosynthesis batch. "
        "The batch is completed once all jobs finish processing."
    ),
    short_help="Check the processing status of a batch.",
)
def _status(
    context: Context,
    batch_id: typing.Annotated[
        str,
        typer.Argument(
            help="Unique batch id to retrieve the current status of.",
            callback=batch_id_callback,
        ),
    ],
) -> None:
    status: BatchStatus = RetroBatchController(context)._status(batch_id)
    progress: float = round(status.completed_jobs / status.number_of_jobs * 100)
    if status.status == "completed":
        console.print(f"[success]\[{progress:>3d}%] Batch completed successfully.")
    elif status.status == "processing":
        console.print(f"[warn]\[{progress:>3d}%] Batch is currently in progress.")
    else:
        console.print(f"[warn]\[{progress:>3d}%] Batch is waiting to be processed.")


# region command: result -----------------------------------------------


@app.command(
    "result",
    help=(
        "Retrieve results for all retrosynthesis jobs in a batch. "
        "Results include synthesizability assessments and a job id that can "
        "be used to get retrosynthetic route details (smiles, depictions)."
    ),
    short_help="Retrieve results for all jobs in a retrosynthesis batch.",
)
def _result(
    context: Context,
    batch_id: typing.Annotated[
        str,
        typer.Argument(
            help="Unique batch id for which to retrieve results.",
            callback=batch_id_callback,
            metavar="BATCH_ID",
        ),
    ],
    output_file: typing.Annotated[
        pathlib.Path,
        typer.Option(
            "--output-file",
            "-o",
            show_default=False,
            help=(
                "Specifies the file for saving JSON results. Defaults to "
                "a timestamped filename created in the current directory."
            ),
            resolve_path=True,
            file_okay=True,
            writable=True,
            dir_okay=False,
        ),
    ] = None,
    count_synthesizable: typing.Annotated[
        bool,
        typer.Option(
            "--summarise",
            is_flag=True,
            help=(
                "Output a summary statistic of how many structures "
                "in the batch are synthesizable."
            ),
        ),
    ] = False,
) -> None:
    controller = RetroBatchController(context)

    # Use default timestamped filename if none provided
    if output_file is None:
        output_file = formatters.create_timestamped_filename(f"{batch_id}_result")

    # first validate that the output file does not already exist, and if
    # it does then confirm overwriting the file with the user and exit
    # if they decline the prompt.
    prompt: str = f"[warn][not b]! Are you sure you want to overwrite: {output_file}?"
    if output_file.exists() and not rich.prompt.Confirm.ask(prompt, console=console):
        raise typer.Exit(0)

    # don't retrieve results unless the batch is completed.
    status: BatchStatus = controller._status(batch_id)
    if status.status != "completed":
        console.print(
            "[warn]! Batch has not completed, try [code]pendingai retro "
            f"batch status {batch_id}[/code] to monitor its status."
        )
        raise typer.Exit(0)

    # retrieve the list of batch results for the batch id from the api
    # controller, check that at least one result was given in return and
    # then write results to a JSON file.
    result: list[BatchJobResult] = controller._result(batch_id)
    if count_synthesizable:
        print(sum([1 for r in result if r.synthesizable]), "of", len(result))
        raise typer.Exit(0)

    console.print(f"[success][not b]✓ Retrieved {len(result)} results successfully.")
    with open(output_file, "w") as fp:
        json.dump([x.model_dump(by_alias=True) for x in result], fp, indent=2)
    filesize: str = formatters.format_filesize(os.path.getsize(output_file))
    console.print(f"[success][not b]✓ Saved results to file: {output_file} ({filesize})")


# region command: list -------------------------------------------------


@app.command(
    "list",
    help=(
        "List all submitted batches in a paginated format. "
        "Each batch contains multiple retrosynthesis jobs submitted together."
    ),
    short_help="List all submitted retrosynthesis batches.",
)
def _list(
    context: Context,
    created_before: typing.Annotated[
        str | None,
        typer.Option(
            "--before",
            help="Batch id resource pointer to retrieve batches created beforehand.",
            callback=batch_id_callback,
        ),
    ] = None,
    created_after: typing.Annotated[
        str | None,
        typer.Option(
            "--after",
            help="Batch id resource pointer to retrieve batches created afterwards.",
            callback=batch_id_callback,
        ),
    ] = None,
    list_size: typing.Annotated[
        int,
        typer.Option(
            "--size",
            "-s",
            help="Size of the retrieved resource list.",
            metavar="INTEGER",
            show_default=False,
            min=1,
            max=100,
        ),
    ] = 10,
) -> None:
    """
    Retrieve a paginated list of submitted batches for a user. Provide
    summary feedback of the page data and help with looking up the next
    offset for a new page.
    """
    # request for the page of batch resources; exit if no batch data was
    # returned in the list with zero status.
    controller = RetroBatchController(context)
    batch_page: BatchPage | None = controller.retrieve_batch_list(
        created_before, created_after, list_size
    )
    if batch_page is None or len(batch_page.data) == 0:
        console.print("[warn]! No batches found.")
        raise typer.Exit(0)

    # build rich table to summarise the batch resources in a minimal and
    # easy to read format; add each row to the table; paged batches are
    # also sorted in chronological descending order from when they were
    # created since page lookup returns batches after that point.
    table = rich.table.Table(
        rich.table.Column("ID"),
        rich.table.Column("Created"),
        rich.table.Column("Filename"),
        rich.table.Column("Jobs", justify="right"),
        box=rich.table.box.SQUARE,
        caption=f"Showing {len(batch_page.data)} result(s).",
    )
    for batch in batch_page.data:
        table.add_row(
            batch.id,
            formatters.localize_datetime(batch.created).isoformat(" ", "seconds"),
            batch.filename if batch.filename is not None else "[i dim]unknown",
            str(batch.number_of_jobs),
        )

    console.print(table)


# region command: delete ----------------------------------------------


@app.command(
    "delete",
    help=(
        "Delete a batch and all its retrosynthesis jobs. "
        "Batches cannot be deleted while in progress."
    ),
    short_help="Delete a completed batch of retrosynthesis jobs.",
)
def _delete(
    context: Context,
    batch_id: typing.Annotated[
        str,
        typer.Argument(
            help="Unique id of the batch being deleted.",
            callback=batch_id_callback,
        ),
    ],
) -> None:
    controller = RetroBatchController(context)
    controller._delete(batch_id)
