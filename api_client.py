"""Cliente HTTP simples para comunicar com o FastAPI backend."""
import urllib.request
import json
from typing import Any


class ApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def _request(self, path: str, method: str = "GET", data: dict | None = None):
        url = f"{self.base_url}{path}"
        body = None
        headers = {}
        if data is not None:
            body = json.dumps(data).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                raw = resp.read().decode("utf-8")
                if not raw:
                    return None
                return json.loads(raw)
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8")
            try:
                return json.loads(raw)
            except Exception:
                return None
        except Exception as e:
            return None

    def get_floors(self) -> list[dict]:
        return self._request("/floors") or []

    def create_floor(self, **kwargs) -> dict | None:
        return self._request("/floors", "POST", kwargs)

    def update_floor(self, floor_id: int, **kwargs) -> dict | None:
        return self._request(f"/floors/{floor_id}", "PUT", kwargs)

    def archive_floor(self, floor_id: int) -> bool:
        res = self._request(f"/floors/{floor_id}", "PATCH", {"is_archived": True})
        return res is not None

    def get_widgets(self, floor_id: int) -> list[dict]:
        return self._request(f"/floors/{floor_id}/widgets") or []

    def create_widget(self, floor_id: int, widget_type: str, config: dict | None = None) -> dict | None:
        return self._request(f"/floors/{floor_id}/widgets", "POST", {
            "floor_id": floor_id,
            "widget_type": widget_type,
            "config": config or {}
        })

    def get_widget_data(self, widget_id: int) -> dict | None:
        return self._request(f"/widgets/{widget_id}/data")

    def save_widget_data(self, widget_id: int, payload: dict) -> bool:
        res = self._request(f"/widgets/{widget_id}/data", "PUT", {"payload": payload})
        return res is not None

    def send_chat(self, floor_id: int, message: str) -> dict | None:
        return self._request("/chat", "POST", {
            "floor_id": floor_id,
            "message": message,
            "role": "user"
        })

    def get_chat_history(self, floor_id: int) -> list[dict]:
        return self._request(f"/floors/{floor_id}/chat") or []
