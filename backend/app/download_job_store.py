"""In-memory store for local model download jobs (shared across clients)."""

from __future__ import annotations

import asyncio
import time
from dataclasses import asdict, dataclass, field
from typing import Literal

DownloadStatus = Literal["idle", "downloading", "completed", "failed"]


@dataclass
class DownloadJob:
    model_id: str
    status: DownloadStatus = "idle"
    bytes_done: int = 0
    bytes_total: int = 0
    error: str | None = None
    message: str | None = None
    started_at: float | None = None
    updated_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        data = asdict(self)
        if self.bytes_total > 0:
            data["percent"] = min(100, round(self.bytes_done / self.bytes_total * 100))
        else:
            data["percent"] = 0
        return data


_jobs: dict[str, DownloadJob] = {}
_lock = asyncio.Lock()
_running: set[str] = set()


async def get_job(model_id: str) -> DownloadJob | None:
    async with _lock:
        return _jobs.get(model_id)


async def list_jobs(active_only: bool = False) -> list[DownloadJob]:
    async with _lock:
        jobs = list(_jobs.values())
    if active_only:
        return [job for job in jobs if job.status == "downloading"]
    return jobs


async def try_start(model_id: str, bytes_total: int) -> tuple[DownloadJob | None, DownloadJob | None]:
    """Start a download job unless one is already running.

    Returns:
        (job, conflict) — conflict is set when status is already downloading.
    """
    async with _lock:
        existing = _jobs.get(model_id)
        if existing and existing.status == "downloading":
            return None, existing

        job = DownloadJob(
            model_id=model_id,
            status="downloading",
            bytes_total=max(bytes_total, 0),
            started_at=time.time(),
        )
        _jobs[model_id] = job
        _running.add(model_id)
        return job, None


async def update_progress(model_id: str, bytes_done: int, bytes_total: int | None = None) -> None:
    async with _lock:
        job = _jobs.get(model_id)
        if not job or job.status != "downloading":
            return
        job.bytes_done = max(0, bytes_done)
        if bytes_total is not None and bytes_total > 0:
            job.bytes_total = bytes_total
        job.updated_at = time.time()


async def finish(model_id: str, *, success: bool, message: str) -> None:
    async with _lock:
        job = _jobs.get(model_id)
        if not job:
            return
        job.status = "completed" if success else "failed"
        job.message = message
        job.error = None if success else message
        if success and job.bytes_total > 0:
            job.bytes_done = job.bytes_total
        job.updated_at = time.time()
        _running.discard(model_id)


async def clear_job(model_id: str) -> None:
    async with _lock:
        _jobs.pop(model_id, None)
        _running.discard(model_id)


def is_running(model_id: str) -> bool:
    return model_id in _running
