"""
Assignment 11 — Audit Log starter (TODO).

Records every interaction for forensics. Never blocks by itself —
other layers catch attacks; this layer makes them reviewable.
"""
from __future__ import annotations

import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path


class AuditLogPlugin:
    """Framework-agnostic audit logger (wire into ADK callbacks or your pipeline)."""

    def __init__(self):
        self.name = "audit_log"
        self.logs: list[dict] = []
        self._open: dict[str, float] = {}

    def record_input(self, *, user_id: str, text: str, request_id: str | None = None):
        """TODO: store input + start timestamp keyed by request_id/user_id."""
        request_id = request_id or str(uuid.uuid4())
        self._open[request_id] = time.monotonic()

        self.logs.append({
            "event": "input",
            "request_id": request_id,
            "user_id": user_id,
            "text": text,
            "timestamp": utc_now_iso(),
        })

        return request_id

    def record_output(
        self,
        *,
        user_id: str,
        text: str,
        blocked: bool = False,
        layer: str | None = None,
        request_id: str | None = None,
    ):
        """TODO: store output, layer decision, latency; append to self.logs."""
        request_id = request_id or str(uuid.uuid4())
        started = self._open.pop(request_id, None)

        latency_ms = None
        if started is not None:
            latency_ms = round((time.monotonic() - started) * 1000, 2)

        self.logs.append({
            "event": "output",
            "request_id": request_id,
            "user_id": user_id,
            "text": text,
            "blocked": blocked,
            "layer": layer,
            "latency_ms": latency_ms,
            "timestamp": utc_now_iso(),
        })

        return request_id

    def export_json(self, filepath: str = "outputs/audit_log.json"):
        """Write logs to disk (JSON array)."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as file:
            json.dump(self.logs, file, ensure_ascii=False, indent=2)

        return str(path)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
