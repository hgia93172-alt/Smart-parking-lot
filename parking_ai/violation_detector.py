"""
parking_ai/violation_detector.py
监控虚拟警戒区域，检测违规停车。
"""
from __future__ import annotations

import time
from typing import Any

from parking_ai.tracker import TrackedObject


def _point_in_polygon(point: tuple[float, float], polygon: list[list[float]]) -> bool:
    """射线法判断点是否在多边形内。"""
    x, y = point
    n = len(polygon)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


class AlertZone:
    """单个警戒区域"""
    def __init__(self, name: str, coords: list[list[float]], threshold_sec: int = 30):
        self.name = name
        self.coords = coords
        self.threshold_sec = threshold_sec
        # {track_id: first_entry_time}
        self._entry_times: dict[int, float] = {}

    def update(self, tracked_objects: list[TrackedObject]) -> list[dict]:
        """检测哪些车辆违规，返回新触发的违规事件列表。"""
        current_ids = set()
        violations = []
        now = time.time()

        for obj in tracked_objects:
            cx, cy = obj.center()
            if _point_in_polygon((cx, cy), self.coords):
                current_ids.add(obj.track_id)
                if obj.track_id not in self._entry_times:
                    self._entry_times[obj.track_id] = now
                else:
                    duration = now - self._entry_times[obj.track_id]
                    if duration >= self.threshold_sec:
                        violations.append({
                            "track_id": obj.track_id,
                            "vehicle_type": obj.vehicle_type,
                            "zone_name": self.name,
                            "duration_seconds": int(duration),
                        })

        # 清理离开区域的车辆
        gone = set(self._entry_times.keys()) - current_ids
        for tid in gone:
            del self._entry_times[tid]

        return violations


class ViolationDetector:
    """管理所有警戒区域，汇总违规事件。"""

    def __init__(self, zones_config: list[dict] | None = None):
        """
        zones_config: 来自 Camera.alert_zones 的配置列表
        [{"name": "消防通道", "coords": [[x,y],...], "threshold_sec": 30}]
        """
        self.zones: list[AlertZone] = []
        if zones_config:
            for z in zones_config:
                self.zones.append(AlertZone(
                    name=z.get("name", "警戒区"),
                    coords=z.get("coords", []),
                    threshold_sec=z.get("threshold_sec", 30),
                ))

    def update(self, tracked_objects: list[TrackedObject]) -> list[dict]:
        """返回本帧所有违规事件列表。"""
        all_violations = []
        for zone in self.zones:
            all_violations.extend(zone.update(tracked_objects))
        return all_violations
