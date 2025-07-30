#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class Batch(BaseModel):
    """
    Batch data model with minimal fields and simple defaults to avoid
    future schema breaking changes and allow incomplete data from the
    api layer to be returned.
    """

    id: str
    object: str
    name: str | None = None
    description: str | None = None
    created: datetime
    updated: datetime
    number_of_jobs: int
    parameters: dict
    filename: str | None = None


class BatchStatus(BaseModel):
    status: str
    number_of_jobs: int
    completed_jobs: int


class BatchPage(BaseModel):
    """
    Paginated container for batches based with added metadata for a
    lookup key offset and a flag for more results in the page response.
    Added model validation will quietly coerce pagination metadata for
    inconsistent paging data.
    """

    data: list[Batch]
    has_more: bool = False


class BatchJobResult(BaseModel):
    """
    Batch job screening result nested data model used to show a single
    results for a retrosynthesis job. No default data is used, jobs need
    to return accurate data so stricter validation is user per command.
    """

    job_id: str
    smiles: str
    completed: bool
    synthesizable: bool
