import gzip
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import threading
import uuid


class LLMResponseLogger:
    """Logs each LLM response as a compressed JSON file under log_storage/<session_id>."""

    def __init__(self, base_path: str | Path = "log_storage"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def _session_dir(self, session_id: str) -> Path:
        d = self.base_path / session_id
        d.mkdir(parents=True, exist_ok=True)
        return d

    def log_response(self, session_id: str, content: str, sender: str, extra: Optional[Dict[str, Any]] = None) -> Path:
        ts = datetime.utcnow().isoformat(timespec="milliseconds") + "Z"
        fname = f"{ts}_{uuid.uuid4().hex[:8]}.json.gz"
        record = {
            "session_id": session_id,
            "sender": sender,
            "created_at": ts,
            "response_length": len(content) if content else 0,
            "metadata": extra or {},
            "content": content,
        }
        payload = json.dumps(record, ensure_ascii=False).encode("utf-8")
        path = self._session_dir(session_id) / fname
        with self._lock:
            with gzip.open(path, "wb") as f:  # type: ignore[arg-type]
                f.write(payload)
        return path

    def list_logs(self, session_id: str) -> list[dict]:
        """Return metadata for all logs in a session (without loading full content)."""
        session_dir = self.base_path / session_id
        if not session_dir.exists():
            return []
        logs = []
        for fp in sorted(session_dir.glob("*.json.gz")):
            # Extract timestamp from filename prefix for ordering
            ts_part = fp.name.split(".json.gz")[0]
            logs.append({
                "file": fp.name,
                "path": str(fp),
                "timestamp": ts_part.split("_")[0],
            })
        return logs

    def read_log(self, session_id: str, filename: str) -> dict | None:
        """Read a specific log file content by filename."""
        fp = self.base_path / session_id / filename
        if not fp.exists():
            return None
        with gzip.open(fp, "rb") as f:  # type: ignore[arg-type]
            return json.loads(f.read().decode("utf-8"))
