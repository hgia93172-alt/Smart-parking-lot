"""
parking_ai/space_monitor.py
基于 IOU 判断车位占用状态。
"""
from __future__ import annotations

from typing import Any

from parking_ai.detector import Detection
from parking_ai.tracker import TrackedObject


def _compute_iou(bbox_a: list[float], bbox_b: list[float]) -> float:
    """计算两个 bounding box 的 IOU 值。"""
    x1 = max(bbox_a[0], bbox_b[0])
    y1 = max(bbox_a[1], bbox_b[1])
    x2 = min(bbox_a[2], bbox_b[2])
    y2 = min(bbox_a[3], bbox_b[3])

    inter_area = max(0, x2 - x1) * max(0, y2 - y1)
    if inter_area == 0:
        return 0.0

    area_a = (bbox_a[2] - bbox_a[0]) * (bbox_a[3] - bbox_a[1])
    area_b = (bbox_b[2] - bbox_b[0]) * (bbox_b[3] - bbox_b[1])
    union_area = area_a + area_b - inter_area
    return inter_area / union_area if union_area > 0 else 0.0


def _polygon_to_bbox(coords: list[list[float]]) -> list[float]:
    """将多边形坐标转换为外接矩形 [x1,y1,x2,y2]。"""
    xs = [p[0] for p in coords]
    ys = [p[1] for p in coords]
    return [min(xs), min(ys), max(xs), max(ys)]


class SpaceMonitor:
    """
    管理停车位的占用检测。
    spaces: list of {"id": int, "space_no": str, "coordinates": [[x,y],...]}
    iou_threshold: IOU 高于此值则判定为占用
    """

    def __init__(self, spaces: list[dict], iou_threshold: float = 0.3):
        self.spaces = spaces
        self.iou_threshold = iou_threshold
        # {space_id: {"status": "available"|"occupied", "track_id": int|None}}
        self._state: dict[int, dict] = {
            s["id"]: {"status": "available", "track_id": None}
            for s in spaces
        }

    def update(self, tracked_objects: list[TrackedObject]) -> list[dict]:
        """
        根据当前所有跟踪到的车辆，更新每个车位的状态。
        返回状态发生变化的车位列表。
        """
        changes = []
        for space in self.spaces:
            sid = space["id"]
            coords = space.get("coordinates")
            if not coords:
                continue
            space_bbox = _polygon_to_bbox(coords)

            occupied = False
            occupying_track_id = None
            for obj in tracked_objects:
                iou = _compute_iou(obj.bbox, space_bbox)
                if iou >= self.iou_threshold:
                    occupied = True
                    occupying_track_id = obj.track_id
                    break

            new_status = "occupied" if occupied else "available"
            prev = self._state[sid]
            if new_status != prev["status"]:
                self._state[sid] = {"status": new_status, "track_id": occupying_track_id}
                changes.append({
                    "space_id": sid,
                    "space_no": space.get("space_no", ""),
                    "prev_status": prev["status"],
                    "new_status": new_status,
                    "track_id": occupying_track_id,
                })

        return changes

    def get_state(self) -> dict[int, dict]:
        return self._state.copy()
