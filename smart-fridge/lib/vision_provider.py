from __future__ import annotations

import random
from typing import Dict, List

from . import db
from .utils import add_days, format_date, stable_hash, today


class MockVisionProvider:
    def __init__(self) -> None:
        self.items = db.list_items()

    def detect(self, image_id: str, top_k: int = 10) -> List[Dict[str, str]]:
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


def get_provider(name: str) -> MockVisionProvider:
    if name != "mock":
        raise ValueError("Only mock provider is supported in offline MVP.")
    return MockVisionProvider()
