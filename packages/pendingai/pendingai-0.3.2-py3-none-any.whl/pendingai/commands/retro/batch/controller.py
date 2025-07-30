#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from __future__ import annotations

import http
import pathlib

import httpx
import pydantic
import rich
import typer
from httpx import Response

from pendingai import config
from pendingai.api import ApiClient
from pendingai.commands.retro.batch.models import (
    Batch,
    BatchJobResult,
    BatchPage,
    BatchStatus,
)
from pendingai.context import Context

console = rich.console.Console(theme=config.RICH_CONSOLE_THEME, soft_wrap=True)


class RetroBatchController:
    """
    Controller for `pendingai retro batch` subcommands. Controls batch
    retrosynthesis operations for captured named commands in the app
    like providing CRUD methods.
    """

    def __init__(self, context: Context) -> None:
        self.context: Context = context
        self.api: ApiClient = ApiClient(
            base_url=config.API_BASE_URLS[self.context.obj.environment],
            subdomain=config.RETRO_SUBDOMAIN,
            bearer_token=self.context.obj.cache.access_token,
        )

    def check_batch_exists(self, id: str) -> bool:
        # check a batch exists by retrieving the resource
        with console.status(f"Checking batch exists: {id}"):
            r: Response = self.api.get(f"/batches/{id}", skip_errors=True)
        return r.status_code == 200

    # region create ----------------------------------------------------

    def create_batch(
        self,
        smiles: list[str],
        input_file: pathlib.Path,
        retrosynthesis_engine: str,
        building_block_libraries: list[str],
        number_of_routes: int,
        processing_time: int,
        reaction_limit: int,
        building_block_limit: int,
        filename: str | None = None,
    ) -> Batch:
        """
        Create a batch of retrosynthesis jobs from an input file and set
        of job parameters by calling the api layer. Parse the response
        into the batch object and handle submission failures.

        Args:
            retrosynthesis_engine (str): Retrosynthesis engine id.
            building_block_libraries (list[str]): Building block library
                ids.
            number_of_routes (int): Maximum number of retrosynthetic
                routes to generate.
            processing_time (int): Maximum processing time in seconds.
            reaction_limit (int): Maximum number of times a specific
                reaction can appear in generated retrosynthetic routes.
            building_block_limit (int): Maximum number of times a
                building block can appear in a retrosynthetic route.
            filename (str, optional): Sanitized filename used for the
                batch submission as added metadata.

        Raises:
            typer.Exit: Failed to submit the batch request with an
                unexpected status code or invalid response data.

        Returns:
            Batch: Submitted batch object.
        """
        # build parameter dict for the request, note that job parameters
        # are not nested and are currently given as snake-case keys.
        body: dict = {
            "parameters": {
                "retrosynthesis_engine": retrosynthesis_engine,
                "building_block_libraries": building_block_libraries,
                "number_of_routes": number_of_routes,
                "processing_time": processing_time,
                "reaction_limit": reaction_limit,
                "building_block_limit": building_block_limit,
            },
            "filename": filename,
        }

        # create a batch resource on an initial request limit
        request_limit: int = 10_000
        with console.status("Creating a new batch..."):
            body["smiles"] = smiles[:request_limit]
            r: Response = self.api.post("/batches", json=body)
        batch: Batch = Batch.model_validate(r.json())
        console.print(f"Created {len(body['smiles'])} jobs to batch: {batch.id}")

        # iterate remaining mini batches as update requests
        for i in range(request_limit, len(smiles), request_limit):
            with console.status("Appending to the new batch..."):
                body = {"smiles": smiles[i : i + request_limit]}
                r = self.api.put(f"/batches/{batch.id}", json=body)
            console.print(f"[not b]Added {len(body['smiles'])} jobs to the batch.")

        return batch

    # region retrieve --------------------------------------------------

    def retrieve_batch_list(
        self,
        created_before: str | None = None,
        created_after: str | None = None,
        list_size: int = 10,
    ) -> BatchPage:
        # build the parameter list depending on which values are set and
        # non-null such as the pointers to before / after ranges
        params: dict = {"size": list_size}
        if created_before:
            params["created-before"] = created_before
        if created_after:
            params["created-after"] = created_after

        with console.status("Retrieving list of batches..."):
            r: httpx.Response = self.api.get("/batches", params=params)

        try:
            return BatchPage.model_validate(r.json())
        except Exception:
            console.print("[fail]Unable to retrieve list of batches.")
            raise typer.Exit(1)

    def _result(self, batch_id: str) -> list[BatchJobResult]:
        """
        Retrieves a list of individual batch job results. Handles edge
        conditions of when a batch is still in progress or a batch does
        not exist.

        Args:
            batch_id (str): Batch resource id.

        Raises:
            typer.Exit: Batch does not exist or is still processing.

        Returns:
            list[BatchJobResult]: Batch results for each job.
        """
        # retrieve the batch results from the api with a console status
        # spinner in case the api call is hanging or times out for being
        # too slow.
        with console.status(f"Retrieving results for {batch_id}"):
            r: httpx.Response = self.api.get(
                f"/batches/{batch_id}/result",
                skip_errors=True,
            )

        if r.status_code == http.HTTPStatus.OK:
            # parse a completed result for the batch iterating over each
            # job result and constructing a set of response objects.
            result: list[BatchJobResult] = []
            for x in r.json():
                try:
                    result.append(BatchJobResult.model_validate(x))
                except pydantic.ValidationError:
                    continue
            return result

        console.print("[warn]! Batch was not found.")
        raise typer.Exit(1)

    # region status ----------------------------------------------------

    def _status(self, id: str) -> BatchStatus:
        with console.status("Retrieving status for batch..."):
            r: Response = self.api.get(f"/batches/{id}/status", skip_errors=True)
        if r.status_code == http.HTTPStatus.OK:
            return BatchStatus.model_validate(r.json())
        console.print("[warn]! Batch status was not found.")
        raise typer.Exit(1)

    # region update ----------------------------------------------------

    # region delete ----------------------------------------------------

    def _delete(self, id: str) -> None:
        with console.status("Deleting batch..."):
            r: Response = self.api.delete(f"/batches/{id}")
        if r.status_code != http.HTTPStatus.OK:
            console.print("[fail]Failed to delete batch, please try again.")
            raise typer.Exit(1)
        console.print("[success]✓ Batch was deleted successfully.")
