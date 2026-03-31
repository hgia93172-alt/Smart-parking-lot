from __future__ import annotations

from decimal import Decimal
from typing import Any

from rest_framework import serializers

from parking.models import (
    BillingRule,
    Camera,
    ParkingLot,
    ParkingSession,
    ParkingSpace,
    VehicleRecord,
    ViolationRecord,
)


# ── ParkingLot ──────────────────────────────────────────────────────────────

class ParkingLotSerializer(serializers.ModelSerializer):
    available_spaces = serializers.SerializerMethodField()
    occupied_spaces = serializers.SerializerMethodField()
    occupancy_rate = serializers.SerializerMethodField()

    class Meta:
        model = ParkingLot
        fields = [
            "id", "name", "address", "total_spaces", "description",
            "is_active", "available_spaces", "occupied_spaces",
            "occupancy_rate", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_available_spaces(self, obj: ParkingLot) -> int:
        return obj.available_spaces

    def get_occupied_spaces(self, obj: ParkingLot) -> int:
        return obj.occupied_spaces

    def get_occupancy_rate(self, obj: ParkingLot) -> float:
        if obj.total_spaces == 0:
            return 0.0
        return round(obj.occupied_spaces / obj.total_spaces * 100, 1)


# ── Camera ───────────────────────────────────────────────────────────────────

class CameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = [
            "id", "lot", "name", "stream_url", "status",
            "alert_zones", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


# ── ParkingSpace ─────────────────────────────────────────────────────────────

class ParkingSpaceSerializer(serializers.ModelSerializer):
    lot_name = serializers.CharField(source="lot.name", read_only=True)
    camera_name = serializers.CharField(source="camera.name", read_only=True, default=None)

    class Meta:
        model = ParkingSpace
        fields = [
            "id", "lot", "lot_name", "space_no", "space_type", "status",
            "coordinates", "camera", "camera_name",
            "occupied_since", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "occupied_since", "created_at", "updated_at"]


class SpaceStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=ParkingSpace.STATUS_CHOICES)


# ── VehicleRecord ─────────────────────────────────────────────────────────────

class VehicleRecordSerializer(serializers.ModelSerializer):
    lot_name = serializers.CharField(source="lot.name", read_only=True, default=None)
    camera_name = serializers.CharField(source="camera.name", read_only=True, default=None)
    direction_label = serializers.CharField(source="get_direction_display", read_only=True)
    vehicle_type_label = serializers.CharField(source="get_vehicle_type_display", read_only=True)

    class Meta:
        model = VehicleRecord
        fields = [
            "id", "lot", "lot_name", "camera", "camera_name",
            "track_id", "license_plate", "vehicle_type", "vehicle_type_label",
            "direction", "direction_label", "confidence",
            "snapshot", "recorded_at",
        ]
        read_only_fields = ["id", "recorded_at"]


class VehicleEntrySerializer(serializers.Serializer):
    lot_id = serializers.IntegerField()
    camera_id = serializers.IntegerField(required=False, allow_null=True)
    track_id = serializers.IntegerField(required=False, allow_null=True)
    license_plate = serializers.CharField(max_length=32, allow_blank=True, default="")
    vehicle_type = serializers.ChoiceField(choices=VehicleRecord.TYPE_CHOICES, default="car")
    confidence = serializers.FloatField(default=0.0)
    space_id = serializers.IntegerField(required=False, allow_null=True)


class VehicleExitSerializer(serializers.Serializer):
    lot_id = serializers.IntegerField()
    camera_id = serializers.IntegerField(required=False, allow_null=True)
    track_id = serializers.IntegerField(required=False, allow_null=True)
    license_plate = serializers.CharField(max_length=32, allow_blank=True, default="")
    vehicle_type = serializers.ChoiceField(choices=VehicleRecord.TYPE_CHOICES, default="car")
    confidence = serializers.FloatField(default=0.0)
    session_id = serializers.IntegerField(required=False, allow_null=True)


# ── ParkingSession ────────────────────────────────────────────────────────────

class ParkingSessionSerializer(serializers.ModelSerializer):
    lot_name = serializers.CharField(source="lot.name", read_only=True, default=None)
    space_no = serializers.CharField(source="space.space_no", read_only=True, default=None)
    status_label = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = ParkingSession
        fields = [
            "id", "lot", "lot_name", "space", "space_no",
            "license_plate", "vehicle_type", "status", "status_label",
            "entry_time", "exit_time", "duration_minutes", "fee", "is_paid",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


# ── ViolationRecord ───────────────────────────────────────────────────────────

class ViolationRecordSerializer(serializers.ModelSerializer):
    lot_name = serializers.CharField(source="lot.name", read_only=True, default=None)
    camera_name = serializers.CharField(source="camera.name", read_only=True, default=None)
    violation_type_label = serializers.CharField(source="get_violation_type_display", read_only=True)
    status_label = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = ViolationRecord
        fields = [
            "id", "lot", "lot_name", "camera", "camera_name",
            "track_id", "license_plate", "violation_type", "violation_type_label",
            "zone_name", "duration_seconds", "snapshot",
            "status", "status_label", "remark",
            "violated_at", "resolved_at", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ViolationResolveSerializer(serializers.Serializer):
    remark = serializers.CharField(max_length=255, allow_blank=True, default="")


# ── BillingRule ───────────────────────────────────────────────────────────────

class BillingRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingRule
        fields = [
            "id", "lot", "vehicle_type", "free_minutes",
            "rate_per_hour", "daily_max", "is_active",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


# ── Stats / Dashboard ─────────────────────────────────────────────────────────

class DashboardOverviewSerializer(serializers.Serializer):
    total_lots = serializers.IntegerField()
    total_spaces = serializers.IntegerField()
    available_spaces = serializers.IntegerField()
    occupied_spaces = serializers.IntegerField()
    occupancy_rate = serializers.FloatField()
    active_sessions = serializers.IntegerField()
    pending_violations = serializers.IntegerField()
    today_entries = serializers.IntegerField()
    today_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
