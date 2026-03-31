from __future__ import annotations

import math
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

from django.db.models import Count, Sum, Q
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request

from django_auth.utils.decorators import admin_required, login_required
from django_main.R import R
from django_utils.utils.log_decorators import log_operation
from parking.models import (
    BillingRule,
    Camera,
    ParkingLot,
    ParkingSession,
    ParkingSpace,
    VehicleRecord,
    ViolationRecord,
)
from parking.serializers import (
    BillingRuleSerializer,
    CameraSerializer,
    DashboardOverviewSerializer,
    ParkingLotSerializer,
    ParkingSessionSerializer,
    ParkingSpaceSerializer,
    SpaceStatusUpdateSerializer,
    VehicleEntrySerializer,
    VehicleExitSerializer,
    VehicleRecordSerializer,
    ViolationRecordSerializer,
    ViolationResolveSerializer,
)


# ── helpers ──────────────────────────────────────────────────────────────────

def _pagination_params(request: Request) -> tuple[bool, int, int]:
    qp = getattr(request, "query_params", {}) or {}
    enabled = "page" in qp or "page_size" in qp
    if not enabled:
        return False, 1, 20
    page = max(1, int(qp.get("page", 1) or 1))
    page_size = min(100, max(1, int(qp.get("page_size", 20) or 20)))
    return True, page, page_size


def _paged(items, *, page: int, page_size: int, total: int) -> dict:
    return {"count": total, "page": page, "page_size": page_size, "results": items}


def _calculate_fee(lot_id: int, vehicle_type: str, duration_minutes: int) -> Decimal:
    """根据计费规则计算停车费用。"""
    rule = BillingRule.objects.filter(
        lot_id=lot_id, vehicle_type=vehicle_type, is_active=True
    ).first()
    if rule is None:
        # 默认: 15分钟免费, 5元/小时, 50元封顶
        free_min = 15
        rate = Decimal("5.00")
        daily_max = Decimal("50.00")
    else:
        free_min = rule.free_minutes
        rate = rule.rate_per_hour
        daily_max = rule.daily_max

    billable_minutes = max(0, duration_minutes - free_min)
    fee = Decimal(str(math.ceil(billable_minutes / 60))) * rate
    return min(fee, daily_max)


# ── ParkingLot Views ──────────────────────────────────────────────────────────

class ParkingLotListView(GenericAPIView):
    serializer_class = ParkingLotSerializer

    @login_required
    def get(self, request: Request):
        qs = ParkingLot.objects.prefetch_related("spaces").order_by("id")
        enabled, page, page_size = _pagination_params(request)
        if not enabled:
            return R.ok(data=ParkingLotSerializer(qs, many=True).data)
        total = qs.count()
        start = (page - 1) * page_size
        items = ParkingLotSerializer(qs[start: start + page_size], many=True).data
        return R.ok(data=_paged(items, page=page, page_size=page_size, total=total))

    @log_operation(action="parking_lot_create", remark="创建停车场")
    @admin_required
    def post(self, request: Request):
        ser = ParkingLotSerializer(data=request.data)
        if not ser.is_valid():
            return R.validation_error(data=ser.errors)
        lot = ser.save()
        return R.ok(data=ParkingLotSerializer(lot).data, msg="创建成功")


class ParkingLotDetailView(GenericAPIView):
    serializer_class = ParkingLotSerializer

    def _get_lot(self, lot_id: int):
        lot = ParkingLot.objects.filter(pk=lot_id).prefetch_related("spaces").first()
        if lot is None:
            return None, R.fail(msg="停车场不存在", code=40401, http_status=status.HTTP_404_NOT_FOUND)
        return lot, None

    @login_required
    def get(self, request: Request, lot_id: int):
        lot, err = self._get_lot(lot_id)
        if err:
            return err
        return R.ok(data=ParkingLotSerializer(lot).data)

    @log_operation(action="parking_lot_update", remark="更新停车场")
    @admin_required
    def put(self, request: Request, lot_id: int):
        lot, err = self._get_lot(lot_id)
        if err:
            return err
        ser = ParkingLotSerializer(lot, data=request.data)
        if not ser.is_valid():
            return R.validation_error(data=ser.errors)
        ser.save()
        return R.ok(data=ParkingLotSerializer(lot).data, msg="更新成功")

    @log_operation(action="parking_lot_update", remark="局部更新停车场")
    @admin_required
    def patch(self, request: Request, lot_id: int):
        lot, err = self._get_lot(lot_id)
        if err:
            return err
        ser = ParkingLotSerializer(lot, data=request.data, partial=True)
        if not ser.is_valid():
            return R.validation_error(data=ser.errors)
        ser.save()
        return R.ok(data=ParkingLotSerializer(lot).data, msg="更新成功")

    @log_operation(action="parking_lot_delete", remark="删除停车场")
    @admin_required
    def delete(self, request: Request, lot_id: int):
        lot, err = self._get_lot(lot_id)
        if err:
            return err
        lot.delete()
        return R.ok(msg="删除成功")


# ── Camera Views ──────────────────────────────────────────────────────────────

class CameraListView(GenericAPIView):
    serializer_class = CameraSerializer

    @login_required
    def get(self, request: Request):
        lot_id = request.query_params.get("lot_id")
        qs = Camera.objects.all().order_by("id")
        if lot_id:
            qs = qs.filter(lot_id=lot_id)
        enabled, page, page_size = _pagination_params(request)
        if not enabled:
            return R.ok(data=CameraSerializer(qs, many=True).data)
        total = qs.count()
        start = (page - 1) * page_size
        items = CameraSerializer(qs[start: start + page_size], many=True).data
        return R.ok(data=_paged(items, page=page, page_size=page_size, total=total))

    @log_operation(action="camera_create", remark="创建摄像头")
    @admin_required
    def post(self, request: Request):
        ser = CameraSerializer(data=request.data)
        if not ser.is_valid():
            return R.validation_error(data=ser.errors)
        cam = ser.save()
        return R.ok(data=CameraSerializer(cam).data, msg="创建成功")


class CameraDetailView(GenericAPIView):
    serializer_class = CameraSerializer

    def _get(self, cam_id: int):
        cam = Camera.objects.filter(pk=cam_id).first()
        if cam is None:
            return None, R.fail(msg="摄像头不存在", code=40401, http_status=status.HTTP_404_NOT_FOUND)
        return cam, None

    @login_required
    def get(self, request: Request, cam_id: int):
        cam, err = self._get(cam_id)
        if err:
            return err
        return R.ok(data=CameraSerializer(cam).data)

    @log_operation(action="camera_update", remark="更新摄像头")
    @admin_required
    def patch(self, request: Request, cam_id: int):
        cam, err = self._get(cam_id)
        if err:
            return err
        ser = CameraSerializer(cam, data=request.data, partial=True)
        if not ser.is_valid():
            return R.validation_error(data=ser.errors)
        ser.save()
        return R.ok(data=CameraSerializer(cam).data, msg="更新成功")

    @log_operation(action="camera_delete", remark="删除摄像头")
    @admin_required
    def delete(self, request: Request, cam_id: int):
        cam, err = self._get(cam_id)
        if err:
            return err
        cam.delete()
        return R.ok(msg="删除成功")


# ── ParkingSpace Views ────────────────────────────────────────────────────────

class ParkingSpaceListView(GenericAPIView):
    serializer_class = ParkingSpaceSerializer

    @login_required
    def get(self, request: Request):
        lot_id = request.query_params.get("lot_id")
        status_filter = request.query_params.get("status")
        qs = ParkingSpace.objects.select_related("lot", "camera").order_by("lot", "space_no")
        if lot_id:
            qs = qs.filter(lot_id=lot_id)
        if status_filter:
            qs = qs.filter(status=status_filter)
        enabled, page, page_size = _pagination_params(request)
        if not enabled:
            return R.ok(data=ParkingSpaceSerializer(qs, many=True).data)
        total = qs.count()
        start = (page - 1) * page_size
        items = ParkingSpaceSerializer(qs[start: start + page_size], many=True).data
        return R.ok(data=_paged(items, page=page, page_size=page_size, total=total))

    @log_operation(action="space_create", remark="创建车位")
    @admin_required
    def post(self, request: Request):
        ser = ParkingSpaceSerializer(data=request.data)
        if not ser.is_valid():
            return R.validation_error(data=ser.errors)
        space = ser.save()
        return R.ok(data=ParkingSpaceSerializer(space).data, msg="创建成功")


class ParkingSpaceDetailView(GenericAPIView):
    serializer_class = ParkingSpaceSerializer

    def _get(self, space_id: int):
        space = ParkingSpace.objects.filter(pk=space_id).select_related("lot", "camera").first()
        if space is None:
            return None, R.fail(msg="车位不存在", code=40401, http_status=status.HTTP_404_NOT_FOUND)
        return space, None

    @login_required
    def get(self, request: Request, space_id: int):
        space, err = self._get(space_id)
        if err:
            return err
        return R.ok(data=ParkingSpaceSerializer(space).data)

    @log_operation(action="space_update", remark="更新车位")
    @admin_required
    def patch(self, request: Request, space_id: int):
        space, err = self._get(space_id)
        if err:
            return err
        ser = ParkingSpaceSerializer(space, data=request.data, partial=True)
        if not ser.is_valid():
            return R.validation_error(data=ser.errors)
        ser.save()
        return R.ok(data=ParkingSpaceSerializer(space).data, msg="更新成功")

    @log_operation(action="space_delete", remark="删除车位")
    @admin_required
    def delete(self, request: Request, space_id: int):
        space, err = self._get(space_id)
        if err:
            return err
        space.delete()
        return R.ok(msg="删除成功")


class ParkingSpaceStatusView(GenericAPIView):
    """AI脚本调用此接口更新车位占用状态"""

    @log_operation(action="space_status_update", remark="AI更新车位状态")
    @login_required
    def patch(self, request: Request, space_id: int):
        space = ParkingSpace.objects.filter(pk=space_id).first()
        if space is None:
            return R.fail(msg="车位不存在", code=40401, http_status=status.HTTP_404_NOT_FOUND)
        ser = SpaceStatusUpdateSerializer(data=request.data)
        if not ser.is_valid():
            return R.validation_error(data=ser.errors)
        new_status = ser.validated_data["status"]
        if new_status == ParkingSpace.STATUS_OCCUPIED and space.status != ParkingSpace.STATUS_OCCUPIED:
            space.occupied_since = timezone.now()
        elif new_status == ParkingSpace.STATUS_AVAILABLE:
            space.occupied_since = None
        space.status = new_status
        space.save()
        return R.ok(data=ParkingSpaceSerializer(space).data, msg="状态更新成功")


# ── VehicleRecord Views ───────────────────────────────────────────────────────

class VehicleRecordListView(GenericAPIView):
    serializer_class = VehicleRecordSerializer

    @login_required
    def get(self, request: Request):
        qp = request.query_params
        qs = VehicleRecord.objects.select_related("lot", "camera").order_by("-id")
        if qp.get("lot_id"):
            qs = qs.filter(lot_id=qp["lot_id"])
        if qp.get("direction"):
            qs = qs.filter(direction=qp["direction"])
        if qp.get("license_plate"):
            qs = qs.filter(license_plate__icontains=qp["license_plate"])
        enabled, page, page_size = _pagination_params(request)
        total = qs.count()
        if not enabled:
            return R.ok(data=VehicleRecordSerializer(qs[:100], many=True).data)
        start = (page - 1) * page_size
        items = VehicleRecordSerializer(qs[start: start + page_size], many=True).data
        return R.ok(data=_paged(items, page=page, page_size=page_size, total=total))


class VehicleEntryView(GenericAPIView):
    """车辆入场（由AI检测脚本或手动调用）"""

    @log_operation(action="vehicle_entry", remark="车辆入场")
    @login_required
    def post(self, request: Request):
        ser = VehicleEntrySerializer(data=request.data)
        if not ser.is_valid():
            return R.validation_error(data=ser.errors)
        data = ser.validated_data

        lot = ParkingLot.objects.filter(pk=data["lot_id"]).first()
        if lot is None:
            return R.fail(msg="停车场不存在")

        # 创建进场记录
        record = VehicleRecord.objects.create(
            lot_id=data["lot_id"],
            camera_id=data.get("camera_id"),
            track_id=data.get("track_id"),
            license_plate=data.get("license_plate", ""),
            vehicle_type=data.get("vehicle_type", "car"),
            direction=VehicleRecord.DIRECTION_ENTRY,
            confidence=data.get("confidence", 0.0),
        )

        # 创建停车会话
        now = timezone.now()
        session = ParkingSession.objects.create(
            lot_id=data["lot_id"],
            space_id=data.get("space_id"),
            entry_record=record,
            license_plate=data.get("license_plate", ""),
            vehicle_type=data.get("vehicle_type", "car"),
            status=ParkingSession.STATUS_ACTIVE,
            entry_time=now,
        )

        # 如果指定车位，标记为占用
        if data.get("space_id"):
            ParkingSpace.objects.filter(pk=data["space_id"]).update(
                status=ParkingSpace.STATUS_OCCUPIED,
                occupied_since=now,
            )

        return R.ok(
            data={"record_id": record.id, "session_id": session.id},
            msg="入场记录成功",
        )


class VehicleExitView(GenericAPIView):
    """车辆出场 + 自动计费"""

    @log_operation(action="vehicle_exit", remark="车辆出场")
    @login_required
    def post(self, request: Request):
        ser = VehicleExitSerializer(data=request.data)
        if not ser.is_valid():
            return R.validation_error(data=ser.errors)
        data = ser.validated_data

        lot = ParkingLot.objects.filter(pk=data["lot_id"]).first()
        if lot is None:
            return R.fail(msg="停车场不存在")

        now = timezone.now()

        # 找到对应的活动会话
        session: ParkingSession | None = None
        if data.get("session_id"):
            session = ParkingSession.objects.filter(pk=data["session_id"], status=ParkingSession.STATUS_ACTIVE).first()
        if session is None and data.get("license_plate"):
            session = ParkingSession.objects.filter(
                lot_id=data["lot_id"],
                license_plate=data["license_plate"],
                status=ParkingSession.STATUS_ACTIVE,
            ).order_by("-id").first()
        if session is None and data.get("track_id"):
            entry = VehicleRecord.objects.filter(
                lot_id=data["lot_id"],
                track_id=data["track_id"],
                direction=VehicleRecord.DIRECTION_ENTRY,
            ).order_by("-id").first()
            if entry:
                session = ParkingSession.objects.filter(
                    entry_record=entry, status=ParkingSession.STATUS_ACTIVE
                ).first()

        # 创建出场记录
        exit_record = VehicleRecord.objects.create(
            lot_id=data["lot_id"],
            camera_id=data.get("camera_id"),
            track_id=data.get("track_id"),
            license_plate=data.get("license_plate", ""),
            vehicle_type=data.get("vehicle_type", "car"),
            direction=VehicleRecord.DIRECTION_EXIT,
            confidence=data.get("confidence", 0.0),
        )

        response_data: dict[str, Any] = {"record_id": exit_record.id}

        if session:
            duration_minutes = max(1, int((now - session.entry_time).total_seconds() / 60))
            fee = _calculate_fee(data["lot_id"], session.vehicle_type, duration_minutes)
            session.exit_record = exit_record
            session.exit_time = now
            session.duration_minutes = duration_minutes
            session.fee = fee
            session.status = ParkingSession.STATUS_COMPLETED
            session.save()
            # 释放车位
            if session.space_id:
                ParkingSpace.objects.filter(pk=session.space_id).update(
                    status=ParkingSpace.STATUS_AVAILABLE,
                    occupied_since=None,
                )
            response_data["session_id"] = session.id
            response_data["duration_minutes"] = duration_minutes
            response_data["fee"] = str(fee)

        return R.ok(data=response_data, msg="出场记录成功")


# ── ParkingSession Views ──────────────────────────────────────────────────────

class ParkingSessionListView(GenericAPIView):
    serializer_class = ParkingSessionSerializer

    @login_required
    def get(self, request: Request):
        qp = request.query_params
        qs = ParkingSession.objects.select_related("lot", "space").order_by("-id")
        if qp.get("lot_id"):
            qs = qs.filter(lot_id=qp["lot_id"])
        if qp.get("status"):
            qs = qs.filter(status=qp["status"])
        if qp.get("license_plate"):
            qs = qs.filter(license_plate__icontains=qp["license_plate"])
        enabled, page, page_size = _pagination_params(request)
        total = qs.count()
        if not enabled:
            return R.ok(data=ParkingSessionSerializer(qs[:100], many=True).data)
        start = (page - 1) * page_size
        items = ParkingSessionSerializer(qs[start: start + page_size], many=True).data
        return R.ok(data=_paged(items, page=page, page_size=page_size, total=total))


class ParkingSessionDetailView(GenericAPIView):
    serializer_class = ParkingSessionSerializer

    @login_required
    def get(self, request: Request, session_id: int):
        session = ParkingSession.objects.filter(pk=session_id).select_related("lot", "space").first()
        if session is None:
            return R.fail(msg="停车记录不存在", code=40401, http_status=status.HTTP_404_NOT_FOUND)
        return R.ok(data=ParkingSessionSerializer(session).data)

    @log_operation(action="session_pay", remark="标记停车缴费")
    @login_required
    def patch(self, request: Request, session_id: int):
        session = ParkingSession.objects.filter(pk=session_id).first()
        if session is None:
            return R.fail(msg="停车记录不存在", code=40401, http_status=status.HTTP_404_NOT_FOUND)
        session.is_paid = True
        session.save()
        return R.ok(data=ParkingSessionSerializer(session).data, msg="缴费成功")


# ── ViolationRecord Views ─────────────────────────────────────────────────────

class ViolationRecordListView(GenericAPIView):
    serializer_class = ViolationRecordSerializer

    @login_required
    def get(self, request: Request):
        qp = request.query_params
        qs = ViolationRecord.objects.select_related("lot", "camera").order_by("-id")
        if qp.get("lot_id"):
            qs = qs.filter(lot_id=qp["lot_id"])
        if qp.get("status"):
            qs = qs.filter(status=qp["status"])
        enabled, page, page_size = _pagination_params(request)
        total = qs.count()
        if not enabled:
            return R.ok(data=ViolationRecordSerializer(qs[:100], many=True).data)
        start = (page - 1) * page_size
        items = ViolationRecordSerializer(qs[start: start + page_size], many=True).data
        return R.ok(data=_paged(items, page=page, page_size=page_size, total=total))

    @log_operation(action="violation_create", remark="上报违规记录")
    @login_required
    def post(self, request: Request):
        ser = ViolationRecordSerializer(data=request.data)
        if not ser.is_valid():
            return R.validation_error(data=ser.errors)
        v = ser.save()
        return R.ok(data=ViolationRecordSerializer(v).data, msg="违规已记录")


class ViolationResolveView(GenericAPIView):
    """标记违规已处理"""

    @log_operation(action="violation_resolve", remark="处理违规记录")
    @admin_required
    def patch(self, request: Request, violation_id: int):
        v = ViolationRecord.objects.filter(pk=violation_id).first()
        if v is None:
            return R.fail(msg="违规记录不存在", code=40401, http_status=status.HTTP_404_NOT_FOUND)
        ser = ViolationResolveSerializer(data=request.data)
        if not ser.is_valid():
            return R.validation_error(data=ser.errors)
        v.status = ViolationRecord.STATUS_RESOLVED
        v.remark = ser.validated_data.get("remark", "")
        v.resolved_at = timezone.now()
        v.save()
        return R.ok(data=ViolationRecordSerializer(v).data, msg="处理成功")


# ── BillingRule Views ─────────────────────────────────────────────────────────

class BillingRuleListView(GenericAPIView):
    serializer_class = BillingRuleSerializer

    @login_required
    def get(self, request: Request):
        lot_id = request.query_params.get("lot_id")
        qs = BillingRule.objects.order_by("lot", "vehicle_type")
        if lot_id:
            qs = qs.filter(lot_id=lot_id)
        return R.ok(data=BillingRuleSerializer(qs, many=True).data)

    @log_operation(action="billing_rule_create", remark="创建计费规则")
    @admin_required
    def post(self, request: Request):
        ser = BillingRuleSerializer(data=request.data)
        if not ser.is_valid():
            return R.validation_error(data=ser.errors)
        rule = ser.save()
        return R.ok(data=BillingRuleSerializer(rule).data, msg="创建成功")


class BillingRuleDetailView(GenericAPIView):
    serializer_class = BillingRuleSerializer

    @login_required
    def get(self, request: Request, rule_id: int):
        rule = BillingRule.objects.filter(pk=rule_id).first()
        if rule is None:
            return R.fail(msg="计费规则不存在", code=40401, http_status=status.HTTP_404_NOT_FOUND)
        return R.ok(data=BillingRuleSerializer(rule).data)

    @log_operation(action="billing_rule_update", remark="更新计费规则")
    @admin_required
    def patch(self, request: Request, rule_id: int):
        rule = BillingRule.objects.filter(pk=rule_id).first()
        if rule is None:
            return R.fail(msg="计费规则不存在", code=40401, http_status=status.HTTP_404_NOT_FOUND)
        ser = BillingRuleSerializer(rule, data=request.data, partial=True)
        if not ser.is_valid():
            return R.validation_error(data=ser.errors)
        ser.save()
        return R.ok(data=BillingRuleSerializer(rule).data, msg="更新成功")

    @log_operation(action="billing_rule_delete", remark="删除计费规则")
    @admin_required
    def delete(self, request: Request, rule_id: int):
        rule = BillingRule.objects.filter(pk=rule_id).first()
        if rule is None:
            return R.fail(msg="计费规则不存在", code=40401, http_status=status.HTTP_404_NOT_FOUND)
        rule.delete()
        return R.ok(msg="删除成功")


# ── Stats / Dashboard Views ───────────────────────────────────────────────────

class StatsOverviewView(GenericAPIView):
    """总体统计仪表盘数据"""

    @login_required
    def get(self, request: Request):
        today = timezone.now().date()
        today_start = timezone.make_aware(datetime.combine(today, datetime.min.time()))

        total_lots = ParkingLot.objects.filter(is_active=True).count()
        all_spaces = ParkingSpace.objects.all()
        total_spaces = all_spaces.count()
        occupied = all_spaces.filter(status=ParkingSpace.STATUS_OCCUPIED).count()
        available = all_spaces.filter(status=ParkingSpace.STATUS_AVAILABLE).count()
        occupancy_rate = round(occupied / total_spaces * 100, 1) if total_spaces else 0.0

        active_sessions = ParkingSession.objects.filter(status=ParkingSession.STATUS_ACTIVE).count()
        pending_violations = ViolationRecord.objects.filter(status=ViolationRecord.STATUS_PENDING).count()
        today_entries = VehicleRecord.objects.filter(
            direction=VehicleRecord.DIRECTION_ENTRY, recorded_at__gte=today_start
        ).count()
        today_revenue_agg = ParkingSession.objects.filter(
            status=ParkingSession.STATUS_COMPLETED,
            exit_time__gte=today_start,
        ).aggregate(total=Sum("fee"))
        today_revenue = today_revenue_agg["total"] or Decimal("0")

        data = {
            "total_lots": total_lots,
            "total_spaces": total_spaces,
            "available_spaces": available,
            "occupied_spaces": occupied,
            "occupancy_rate": occupancy_rate,
            "active_sessions": active_sessions,
            "pending_violations": pending_violations,
            "today_entries": today_entries,
            "today_revenue": today_revenue,
        }
        return R.ok(data=data)


class StatsHourlyView(GenericAPIView):
    """过去24小时每小时车流量"""

    @login_required
    def get(self, request: Request):
        now = timezone.now()
        start = now - timedelta(hours=24)
        records = VehicleRecord.objects.filter(recorded_at__gte=start)

        # 按小时聚合
        hourly: dict[int, dict] = {}
        for i in range(24):
            h = (start + timedelta(hours=i)).hour
            hourly[i] = {"hour": h, "entries": 0, "exits": 0}

        for record in records:
            diff_hours = int((record.recorded_at - start).total_seconds() / 3600)
            if 0 <= diff_hours < 24:
                if record.direction == VehicleRecord.DIRECTION_ENTRY:
                    hourly[diff_hours]["entries"] += 1
                else:
                    hourly[diff_hours]["exits"] += 1

        return R.ok(data=list(hourly.values()))


class StatsRevenueView(GenericAPIView):
    """收费统计（日报/月报）"""

    @login_required
    def get(self, request: Request):
        period = request.query_params.get("period", "daily")  # daily | monthly
        now = timezone.now()

        if period == "monthly":
            # 最近12个月
            results = []
            for i in range(11, -1, -1):
                d = now.date().replace(day=1) - timedelta(days=i * 30)
                month_start = timezone.make_aware(datetime(d.year, d.month, 1))
                if d.month == 12:
                    month_end = timezone.make_aware(datetime(d.year + 1, 1, 1))
                else:
                    month_end = timezone.make_aware(datetime(d.year, d.month + 1, 1))
                agg = ParkingSession.objects.filter(
                    status=ParkingSession.STATUS_COMPLETED,
                    exit_time__gte=month_start,
                    exit_time__lt=month_end,
                ).aggregate(total=Sum("fee"), count=Count("id"))
                results.append({
                    "label": f"{d.year}-{d.month:02d}",
                    "revenue": str(agg["total"] or 0),
                    "count": agg["count"] or 0,
                })
            return R.ok(data=results)
        else:
            # 最近7天
            results = []
            for i in range(6, -1, -1):
                day = now.date() - timedelta(days=i)
                day_start = timezone.make_aware(datetime.combine(day, datetime.min.time()))
                day_end = day_start + timedelta(days=1)
                agg = ParkingSession.objects.filter(
                    status=ParkingSession.STATUS_COMPLETED,
                    exit_time__gte=day_start,
                    exit_time__lt=day_end,
                ).aggregate(total=Sum("fee"), count=Count("id"))
                results.append({
                    "label": str(day),
                    "revenue": str(agg["total"] or 0),
                    "count": agg["count"] or 0,
                })
            return R.ok(data=results)


class LotDashboardView(GenericAPIView):
    """单个停车场仪表盘"""

    @login_required
    def get(self, request: Request, lot_id: int):
        lot = ParkingLot.objects.filter(pk=lot_id).prefetch_related("spaces").first()
        if lot is None:
            return R.fail(msg="停车场不存在", code=40401, http_status=status.HTTP_404_NOT_FOUND)

        spaces = list(lot.spaces.all())
        space_data = []
        for s in spaces:
            space_data.append({
                "id": s.id,
                "space_no": s.space_no,
                "space_type": s.space_type,
                "status": s.status,
                "occupied_since": s.occupied_since,
            })
        active_violations = ViolationRecord.objects.filter(
            lot_id=lot_id, status=ViolationRecord.STATUS_PENDING
        ).count()

        return R.ok(data={
            "lot": ParkingLotSerializer(lot).data,
            "spaces": space_data,
            "pending_violations": active_violations,
        })
