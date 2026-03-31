"""
parking_ai/detector.py
YOLOv11 检测器封装。无模型文件时自动降级为模拟模式。
"""
from __future__ import annotations

import random
import time
from typing import Any

try:
    from ultralytics import YOLO
    _YOLO_AVAILABLE = True
except ImportError:
    _YOLO_AVAILABLE = False


VEHICLE_CLASSES = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}


class Detection:
    __slots__ = ("bbox", "confidence", "class_id", "vehicle_type")

    def __init__(self, bbox: list[float], confidence: float, class_id: int, vehicle_type: str):
        self.bbox = bbox          # [x1, y1, x2, y2]
        self.confidence = confidence
        self.class_id = class_id
        self.vehicle_type = vehicle_type

    def __repr__(self) -> str:
        return f"Detection({self.vehicle_type}, conf={self.confidence:.2f}, bbox={self.bbox})"


class YOLODetector:
    def __init__(self, model_path: str | None = None, confidence: float = 0.4, simulate: bool = False):
        self.confidence = confidence
        self.simulate = simulate or not _YOLO_AVAILABLE or model_path is None

        if not self.simulate:
            try:
                self.model = YOLO(model_path)
                print(f"[Detector] 加载 YOLO 模型: {model_path}")
            except Exception as e:
                print(f"[Detector] 加载模型失败: {e}，切换到模拟模式")
                self.simulate = True
        else:
            print("[Detector] 运行在模拟模式（无须模型文件）")

    def detect(self, frame: Any) -> list[Detection]:
        """对单帧图像进行目标检测，返回检测结果列表。"""
        if self.simulate:
            return self._simulate_detect()
        return self._real_detect(frame)

    def _simulate_detect(self) -> list[Detection]:
        """随机生成模拟检测结果，用于演示。"""
        count = random.randint(0, 4)
        results = []
        for _ in range(count):
            x1 = random.randint(0, 800)
            y1 = random.randint(0, 600)
            x2 = x1 + random.randint(80, 160)
            y2 = y1 + random.randint(50, 100)
            class_id = random.choice(list(VEHICLE_CLASSES.keys()))
            results.append(Detection(
                bbox=[x1, y1, x2, y2],
                confidence=round(random.uniform(0.5, 0.98), 2),
                class_id=class_id,
                vehicle_type=VEHICLE_CLASSES[class_id],
            ))
        return results

    def _real_detect(self, frame: Any) -> list[Detection]:
        """真实 YOLO 推理。"""
        results = self.model(frame, conf=self.confidence, verbose=False)[0]
        detections = []
        for box in results.boxes:
            cls_id = int(box.cls[0])
            if cls_id not in VEHICLE_CLASSES:
                continue
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            detections.append(Detection(
                bbox=[x1, y1, x2, y2],
                confidence=float(box.conf[0]),
                class_id=cls_id,
                vehicle_type=VEHICLE_CLASSES[cls_id],
            ))
        return detections
