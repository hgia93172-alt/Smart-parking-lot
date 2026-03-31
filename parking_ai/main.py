"""
parking_ai/main.py
AI 检测主入口；支持 --simulate 参数在无模型文件时演示。

使用示例：
    python parking_ai/main.py --simulate --lot-id 1 --token YOUR_TOKEN
"""
from __future__ import annotations

import argparse
import logging
import os
import random
import sys
import time

# 确保根目录在 path 中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parking_ai.api_client import ParkingAPIClient
from parking_ai.billing import calculate_fee, format_duration
from parking_ai.detector import YOLODetector
from parking_ai.space_monitor import SpaceMonitor
from parking_ai.tracker import DeepSORTTracker
from parking_ai.violation_detector import ViolationDetector

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description="YOLO 智能停车场检测主程序")
    parser.add_argument("--simulate", action="store_true", help="模拟模式（无需 YOLO 模型文件）")
    parser.add_argument("--model", default=None, help="YOLO 模型权重文件路径（.pt）")
    parser.add_argument("--source", default="0", help="视频源：摄像头编号/RTSP地址/本地文件路径")
    parser.add_argument("--lot-id", type=int, default=1, help="停车场 ID")
    parser.add_argument("--camera-id", type=int, default=None, help="摄像头 ID")
    parser.add_argument("--token", default="", help="API Token")
    parser.add_argument("--backend", default="http://127.0.0.1:8000", help="Django 后端地址")
    parser.add_argument("--fps", type=float, default=10.0, help="处理帧率（模拟模式下每秒虚拟帧数）")
    parser.add_argument("--dry-run", action="store_true", help="不发送 API 请求（仅打印）")
    return parser.parse_args()


def demo_spaces(lot_id: int) -> list[dict]:
    """在演示/模拟模式下生成虚拟车位配置。"""
    return [
        {"id": i, "space_no": f"A-{i:02d}", "coordinates": [
            [50 + (i - 1) * 110, 100],
            [140 + (i - 1) * 110, 100],
            [140 + (i - 1) * 110, 220],
            [50 + (i - 1) * 110, 220],
        ]} for i in range(1, 9)
    ]


def demo_alert_zones() -> list[dict]:
    return [
        {"name": "消防通道", "coords": [[0, 0], [100, 0], [100, 50], [0, 50]], "threshold_sec": 5},
    ]


def main():
    args = parse_args()

    logger.info("=== 智能停车场检测系统启动 ===")
    logger.info("停车场 ID: %d | 模拟模式: %s", args.lot_id, args.simulate)

    detector = YOLODetector(model_path=args.model, simulate=args.simulate)
    tracker = DeepSORTTracker(simulate=args.simulate)
    spaces = demo_spaces(args.lot_id)
    space_monitor = SpaceMonitor(spaces=spaces, iou_threshold=0.3)
    violation_detector = ViolationDetector(zones_config=demo_alert_zones())
    api = ParkingAPIClient(
        base_url=args.backend,
        token=args.token,
        lot_id=args.lot_id,
        dry_run=args.dry_run or not args.token,
    )

    frame_interval = 1.0 / args.fps
    frame_count = 0
    prev_track_ids: set[int] = set()

    logger.info("开始处理视频流（按 Ctrl+C 退出）...")
    try:
        while True:
            loop_start = time.time()

            # --- 检测 ---
            detections = detector.detect(frame=None)

            # --- 跟踪 ---
            tracked = tracker.update(detections)
            current_ids = {t.track_id for t in tracked}

            # --- 检测入场（新出现的 track_id）---
            entered = current_ids - prev_track_ids
            for obj in tracked:
                if obj.track_id in entered:
                    logger.info("  ↑ 车辆入场: track_id=%d type=%s", obj.track_id, obj.vehicle_type)
                    api.report_entry(
                        track_id=obj.track_id,
                        vehicle_type=obj.vehicle_type,
                        confidence=obj.confidence,
                        camera_id=args.camera_id,
                    )

            # --- 检测出场（消失的 track_id）---
            exited = prev_track_ids - current_ids
            for tid in exited:
                logger.info("  ↓ 车辆出场: track_id=%d", tid)
                api.report_exit(
                    track_id=tid,
                    vehicle_type="car",  # 出场时类型已记录在后端
                    confidence=0.9,
                    camera_id=args.camera_id,
                )

            prev_track_ids = current_ids

            # --- 车位状态更新 ---
            changes = space_monitor.update(tracked)
            for ch in changes:
                logger.info("  🅿 车位 %s: %s → %s", ch["space_no"], ch["prev_status"], ch["new_status"])
                api.update_space_status(ch["space_id"], ch["new_status"])

            # --- 违规检测 ---
            violations = violation_detector.update(tracked)
            for v in violations:
                logger.warning("  ⚠ 违规: track_id=%d 在 [%s] 停留 %d 秒",
                               v["track_id"], v["zone_name"], v["duration_seconds"])
                api.report_violation(
                    track_id=v["track_id"],
                    violation_type="fire_lane",
                    zone_name=v["zone_name"],
                    duration_seconds=v["duration_seconds"],
                    camera_id=args.camera_id,
                )

            frame_count += 1
            if frame_count % 100 == 0:
                logger.info("已处理 %d 帧 | 当前跟踪车辆数: %d", frame_count, len(current_ids))

            elapsed = time.time() - loop_start
            sleep_time = max(0, frame_interval - elapsed)
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        logger.info("检测程序已停止。共处理 %d 帧。", frame_count)


if __name__ == "__main__":
    main()
