"""
parking_ai/tracker.py
DeepSORT 多目标跟踪器封装。无依赖时降级为简单 ID 分配模拟。
"""
from __future__ import annotations

import random
from typing import Any

from parking_ai.detector import Detection

try:
    from deep_sort_realtime.deepsort_tracker import DeepSort
    _DEEPSORT_AVAILABLE = True
except ImportError:
    _DEEPSORT_AVAILABLE = False


class TrackedObject:
    __slots__ = ("track_id", "bbox", "vehicle_type", "confidence")

    def __init__(self, track_id: int, bbox: list[float], vehicle_type: str, confidence: float):
        self.track_id = track_id
        self.bbox = bbox
        self.vehicle_type = vehicle_type
        self.confidence = confidence

    def center(self) -> tuple[float, float]:
        x1, y1, x2, y2 = self.bbox
        return (x1 + x2) / 2, (y1 + y2) / 2

    def __repr__(self) -> str:
        return f"TrackedObject(id={self.track_id}, type={self.vehicle_type})"


class DeepSORTTracker:
    def __init__(self, simulate: bool = False, max_age: int = 30):
        self.simulate = simulate or not _DEEPSORT_AVAILABLE
        self._next_id = 1
        self._sim_tracks: dict[int, TrackedObject] = {}

        if not self.simulate:
            try:
                self.tracker = DeepSort(max_age=max_age)
                print("[Tracker] 加载 DeepSORT 跟踪器")
            except Exception as e:
                print(f"[Tracker] 初始化失败: {e}，切换到模拟模式")
                self.simulate = True
        else:
            print("[Tracker] 运行在模拟模式")

    def update(self, detections: list[Detection], frame: Any = None) -> list[TrackedObject]:
        if self.simulate:
            return self._simulate_update(detections)
        return self._real_update(detections, frame)

    def _simulate_update(self, detections: list[Detection]) -> list[TrackedObject]:
        """简单模拟：给每个检测框分配一个持久ID。"""
        # 简化：每帧随机保留部分已有轨迹 + 新增
        surviving = {k: v for k, v in self._sim_tracks.items() if random.random() > 0.2}
        result = list(surviving.values())

        for det in detections:
            new_id = self._next_id
            self._next_id += 1
            obj = TrackedObject(
                track_id=new_id,
                bbox=det.bbox,
                vehicle_type=det.vehicle_type,
                confidence=det.confidence,
            )
            surviving[new_id] = obj
            result.append(obj)

        self._sim_tracks = surviving
        return result

    def _real_update(self, detections: list[Detection], frame: Any) -> list[TrackedObject]:
        raw = [
            ([d.bbox[0], d.bbox[1], d.bbox[2] - d.bbox[0], d.bbox[3] - d.bbox[1]], d.confidence, d.vehicle_type)
            for d in detections
        ]
        tracks = self.tracker.update_tracks(raw, frame=frame)
        result = []
        for t in tracks:
            if not t.is_confirmed():
                continue
            ltrb = t.to_ltrb()
            result.append(TrackedObject(
                track_id=t.track_id,
                bbox=list(ltrb),
                vehicle_type=str(t.det_class) if t.det_class else "car",
                confidence=t.det_conf if t.det_conf else 0.5,
            ))
        return result
