"""
parking_ai/api_client.py
向 Django 后端 REST API 推送检测结果。
"""
from __future__ import annotations

import json
import logging
from typing import Any

try:
    import requests
    _REQUESTS_AVAILABLE = True
except ImportError:
    _REQUESTS_AVAILABLE = False

logger = logging.getLogger(__name__)


class ParkingAPIClient:
    def __init__(self, base_url: str, token: str, lot_id: int, dry_run: bool = False):
        """
        base_url: Django 后端地址，例如 http://127.0.0.1:8000
        token: DRF Token 认证字符串
        lot_id: 当前停车场 ID
        dry_run: 若为 True 则只打印，不发网络请求（用于离线测试）
        """
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.lot_id = lot_id
        self.dry_run = dry_run or not _REQUESTS_AVAILABLE
        self._headers = {"Authorization": f"Token {token}", "Content-Type": "application/json"}

    def _post(self, path: str, payload: dict) -> dict | None:
        url = f"{self.base_url}{path}"
        if self.dry_run:
            logger.info("[DRY] POST %s: %s", url, json.dumps(payload, ensure_ascii=False))
            return None
        try:
            resp = requests.post(url, json=payload, headers=self._headers, timeout=5)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error("API 请求失败: %s %s", url, e)
            return None

    def _patch(self, path: str, payload: dict) -> dict | None:
        url = f"{self.base_url}{path}"
        if self.dry_run:
            logger.info("[DRY] PATCH %s: %s", url, json.dumps(payload, ensure_ascii=False))
            return None
        try:
            resp = requests.patch(url, json=payload, headers=self._headers, timeout=5)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error("API 请求失败: %s %s", url, e)
            return None

    def report_entry(self, track_id: int, vehicle_type: str, confidence: float,
                     camera_id: int | None = None, space_id: int | None = None) -> dict | None:
        """上报车辆入场事件。"""
        payload = {
            "lot_id": self.lot_id,
            "track_id": track_id,
            "vehicle_type": vehicle_type,
            "confidence": confidence,
        }
        if camera_id:
            payload["camera_id"] = camera_id
        if space_id:
            payload["space_id"] = space_id
        return self._post("/api/parking/vehicles/entry/", payload)

    def report_exit(self, track_id: int, vehicle_type: str, confidence: float,
                    camera_id: int | None = None) -> dict | None:
        """上报车辆出场事件。"""
        payload = {
            "lot_id": self.lot_id,
            "track_id": track_id,
            "vehicle_type": vehicle_type,
            "confidence": confidence,
        }
        if camera_id:
            payload["camera_id"] = camera_id
        return self._post("/api/parking/vehicles/exit/", payload)

    def update_space_status(self, space_id: int, new_status: str) -> dict | None:
        """更新车位占用状态。"""
        return self._patch(f"/api/parking/spaces/{space_id}/status/", {"status": new_status})

    def report_violation(self, track_id: int, violation_type: str, zone_name: str,
                         duration_seconds: int, camera_id: int | None = None) -> dict | None:
        """上报违规停车记录。"""
        import datetime
        payload = {
            "lot": self.lot_id,
            "track_id": track_id,
            "violation_type": violation_type,
            "zone_name": zone_name,
            "duration_seconds": duration_seconds,
            "violated_at": datetime.datetime.now().isoformat(),
        }
        if camera_id:
            payload["camera"] = camera_id
        return self._post("/api/parking/violations/", payload)
