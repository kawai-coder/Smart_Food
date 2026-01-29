from __future__ import annotations

import base64
import json
import os
import random
from typing import Any, Dict, List

import requests

from . import db
from .utils import add_days, format_date, stable_hash, today


class ProviderNotAvailable(Exception):
    def __init__(self, code: str, reason: str) -> None:
        super().__init__(reason)
        self.code = code
        self.reason = reason


class BaseVisionProvider:
    id: str
    name: str

    def is_available(self) -> tuple[bool, str]:
        raise NotImplementedError

    def detect(self, image_id: str, top_k: int = 10) -> List[Dict[str, Any]]:
        raise NotImplementedError


class MockVisionProvider(BaseVisionProvider):
    id = "mock"
    name = "Mock (Offline)"

    def __init__(self) -> None:
        self.items = db.list_items()

    def is_available(self) -> tuple[bool, str]:
        return True, ""

    def detect(self, image_id: str, top_k: int = 10) -> List[Dict[str, Any]]:
        if not self.items:
            return []
        rng = random.Random(stable_hash(image_id))
        sample_size = min(top_k, max(6, min(10, len(self.items))))
        candidates = rng.sample(self.items, k=min(sample_size, len(self.items)))
        detections = []
        for item in candidates:
            confidence = round(rng.uniform(0.6, 0.95), 2)
            quantity = round(rng.uniform(1, 4), 1)
            shelf_life = item.get("shelf_life_days_default") or 5
            expire_date = format_date(add_days(today(), shelf_life))
            detections.append(
                {
                    "temp_id": f"det_{item['item_id']}_{stable_hash(image_id)}",
                    "item_id": item["item_id"],
                    "item_name": item["name"],
                    "confidence": confidence,
                    "quantity": quantity,
                    "unit": item.get("default_unit") or "unit",
                    "suggest_expire_date": expire_date,
                    "location": "fridge",
                }
            )
        return detections


class HttpVisionProvider(BaseVisionProvider):
    id = "http"
    name = "HTTP Vision (Generic)"

    def __init__(self) -> None:
        self.endpoint = os.getenv("VISION_HTTP_ENDPOINT")
        self.headers_json = os.getenv("VISION_HTTP_HEADERS_JSON", "")
        timeout = os.getenv("VISION_HTTP_TIMEOUT", "20")
        self.timeout = int(timeout) if timeout.isdigit() else 20

    def is_available(self) -> tuple[bool, str]:
        if not self.endpoint:
            return False, "VISION_HTTP_ENDPOINT is not configured"
        return True, ""

    def _headers(self) -> Dict[str, str]:
        if not self.headers_json:
            return {"Content-Type": "application/json"}
        try:
            headers = json.loads(self.headers_json)
            headers["Content-Type"] = "application/json"
            return headers
        except json.JSONDecodeError as exc:
            raise ProviderNotAvailable("PROVIDER_CONFIG_ERROR", f"Invalid VISION_HTTP_HEADERS_JSON: {exc}") from exc

    def detect(self, image_id: str, top_k: int = 10) -> List[Dict[str, Any]]:
        available, reason = self.is_available()
        if not available:
            raise ProviderNotAvailable("PROVIDER_NOT_AVAILABLE", reason)
        image = db.get_image(image_id)
        if not image:
            raise ProviderNotAvailable("IMAGE_NOT_FOUND", f"Image {image_id} not found")
        file_path = image.get("file_path")
        if not file_path or not os.path.exists(file_path):
            raise ProviderNotAvailable("IMAGE_NOT_FOUND", f"Image file missing for {image_id}")
        with open(file_path, "rb") as file_handle:
            image_base64 = base64.b64encode(file_handle.read()).decode("utf-8")
        payload = {"image_id": image_id, "image_base64": image_base64, "top_k": top_k}
        response = requests.post(
            self.endpoint,
            headers=self._headers(),
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        detections = data.get("detections", [])
        items = {item["name"]: item for item in db.list_items()}
        normalized = []
        for idx, det in enumerate(detections):
            name = det.get("name") or det.get("item_name") or "未知"
            item = items.get(name)
            suggest_expire_date = det.get("suggest_expire_date")
            if not suggest_expire_date and det.get("suggest_expire_days") is not None:
                try:
                    days = int(det.get("suggest_expire_days"))
                    suggest_expire_date = format_date(add_days(today(), days))
                except (ValueError, TypeError):
                    suggest_expire_date = None
            normalized.append(
                {
                    "temp_id": det.get("temp_id") or f"det_http_{image_id}_{idx}",
                    "item_id": item["item_id"] if item else None,
                    "item_name": item["name"] if item else name,
                    "confidence": det.get("confidence", 0.0),
                    "quantity": det.get("quantity", 1),
                    "unit": det.get("unit") or (item.get("default_unit") if item else "unit"),
                    "suggest_expire_date": suggest_expire_date,
                    "location": det.get("location", "fridge"),
                }
            )
        return normalized


def list_providers() -> Dict[str, BaseVisionProvider]:
    return {
        MockVisionProvider.id: MockVisionProvider(),
        HttpVisionProvider.id: HttpVisionProvider(),
    }


def get_provider(name: str) -> BaseVisionProvider:
    providers = list_providers()
    if name not in providers:
        raise ProviderNotAvailable("PROVIDER_NOT_FOUND", f"Provider '{name}' not registered")
    provider = providers[name]
    available, reason = provider.is_available()
    if not available:
        raise ProviderNotAvailable("PROVIDER_NOT_AVAILABLE", reason)
    return provider
