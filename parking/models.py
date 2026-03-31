from __future__ import annotations

from django.conf import settings
from django.db import models


class ParkingLot(models.Model):
    """停车场基本信息"""

    name = models.CharField(max_length=128, verbose_name="停车场名称", db_comment="停车场名称")
    address = models.CharField(max_length=255, blank=True, default="", verbose_name="地址", db_comment="地址")
    total_spaces = models.IntegerField(default=0, verbose_name="总车位数", db_comment="总车位数")
    description = models.CharField(max_length=500, blank=True, default="", verbose_name="描述")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "停车场"
        verbose_name_plural = "停车场"
        ordering = ["-id"]

    def __str__(self) -> str:
        return f"ParkingLot(id={self.id}, name={self.name})"

    @property
    def available_spaces(self) -> int:
        return self.spaces.filter(status="available").count()

    @property
    def occupied_spaces(self) -> int:
        return self.spaces.filter(status="occupied").count()


class ParkingSpace(models.Model):
    """单个车位"""

    STATUS_AVAILABLE = "available"
    STATUS_OCCUPIED = "occupied"
    STATUS_DISABLED = "disabled"
    STATUS_CHOICES = [
        (STATUS_AVAILABLE, "空闲"),
        (STATUS_OCCUPIED, "占用"),
        (STATUS_DISABLED, "禁用"),
    ]

    TYPE_SMALL = "small"
    TYPE_LARGE = "large"
    TYPE_DISABLED = "disabled_person"
    TYPE_CHOICES = [
        (TYPE_SMALL, "小型车"),
        (TYPE_LARGE, "大型车"),
        (TYPE_DISABLED, "无障碍"),
    ]

    lot = models.ForeignKey(
        ParkingLot,
        on_delete=models.CASCADE,
        related_name="spaces",
        verbose_name="所属停车场",
    )
    space_no = models.CharField(max_length=32, verbose_name="车位编号", db_comment="车位编号（如 A-01）")
    space_type = models.CharField(max_length=32, choices=TYPE_CHOICES, default=TYPE_SMALL, verbose_name="车位类型")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_AVAILABLE, verbose_name="状态")
    # 车位在摄像头画面中的坐标区域，JSON格式: [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
    coordinates = models.JSONField(null=True, blank=True, verbose_name="坐标区域")
    camera = models.ForeignKey(
        "Camera",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="spaces",
        verbose_name="关联摄像头",
    )
    occupied_since = models.DateTimeField(null=True, blank=True, verbose_name="占用开始时间")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "车位"
        verbose_name_plural = "车位"
        ordering = ["lot", "space_no"]
        unique_together = [["lot", "space_no"]]

    def __str__(self) -> str:
        return f"ParkingSpace(id={self.id}, no={self.space_no}, status={self.status})"


class Camera(models.Model):
    """摄像头配置"""

    STATUS_ONLINE = "online"
    STATUS_OFFLINE = "offline"
    STATUS_CHOICES = [
        (STATUS_ONLINE, "在线"),
        (STATUS_OFFLINE, "离线"),
    ]

    lot = models.ForeignKey(
        ParkingLot,
        on_delete=models.CASCADE,
        related_name="cameras",
        verbose_name="所属停车场",
    )
    name = models.CharField(max_length=64, verbose_name="摄像头名称")
    stream_url = models.CharField(max_length=512, blank=True, default="", verbose_name="视频流地址（RTSP/文件路径）")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_OFFLINE, verbose_name="状态")
    # 消防通道/禁停区警戒区域，JSON format: [{"name": "消防通道", "coords": [[x,y],...], "threshold_sec": 30}]
    alert_zones = models.JSONField(null=True, blank=True, verbose_name="警戒区域配置")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "摄像头"
        verbose_name_plural = "摄像头"
        ordering = ["-id"]

    def __str__(self) -> str:
        return f"Camera(id={self.id}, name={self.name})"


class VehicleRecord(models.Model):
    """车辆进出记录"""

    DIRECTION_ENTRY = "entry"
    DIRECTION_EXIT = "exit"
    DIRECTION_CHOICES = [
        (DIRECTION_ENTRY, "入场"),
        (DIRECTION_EXIT, "出场"),
    ]

    TYPE_CAR = "car"
    TYPE_TRUCK = "truck"
    TYPE_BUS = "bus"
    TYPE_MOTORCYCLE = "motorcycle"
    TYPE_CHOICES = [
        (TYPE_CAR, "小型车"),
        (TYPE_TRUCK, "货车"),
        (TYPE_BUS, "大型车/公交"),
        (TYPE_MOTORCYCLE, "摩托车"),
    ]

    lot = models.ForeignKey(
        ParkingLot,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vehicle_records",
        verbose_name="停车场",
    )
    camera = models.ForeignKey(
        Camera,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vehicle_records",
        verbose_name="摄像头",
    )
    track_id = models.IntegerField(null=True, blank=True, verbose_name="跟踪ID", db_comment="DeepSORT分配的唯一ID")
    license_plate = models.CharField(max_length=32, blank=True, default="", verbose_name="车牌号")
    vehicle_type = models.CharField(max_length=32, choices=TYPE_CHOICES, default=TYPE_CAR, verbose_name="车辆类型")
    direction = models.CharField(max_length=8, choices=DIRECTION_CHOICES, verbose_name="方向")
    confidence = models.FloatField(default=0.0, verbose_name="识别置信度")
    snapshot = models.ImageField(upload_to="parking/snapshots/%Y/%m/%d/", null=True, blank=True, verbose_name="截图")
    recorded_at = models.DateTimeField(auto_now_add=True, verbose_name="记录时间")

    class Meta:
        verbose_name = "车辆进出记录"
        verbose_name_plural = "车辆进出记录"
        ordering = ["-id"]

    def __str__(self) -> str:
        return f"VehicleRecord(id={self.id}, plate={self.license_plate}, dir={self.direction})"


class ParkingSession(models.Model):
    """停车会话（对应一次完整停车过程）"""

    STATUS_ACTIVE = "active"
    STATUS_COMPLETED = "completed"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "停车中"),
        (STATUS_COMPLETED, "已离场"),
    ]

    lot = models.ForeignKey(
        ParkingLot,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sessions",
        verbose_name="停车场",
    )
    space = models.ForeignKey(
        ParkingSpace,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sessions",
        verbose_name="车位",
    )
    entry_record = models.OneToOneField(
        VehicleRecord,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="session_as_entry",
        verbose_name="入场记录",
    )
    exit_record = models.OneToOneField(
        VehicleRecord,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="session_as_exit",
        verbose_name="出场记录",
    )
    license_plate = models.CharField(max_length=32, blank=True, default="", verbose_name="车牌号")
    vehicle_type = models.CharField(max_length=32, default="car", verbose_name="车辆类型")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_ACTIVE, verbose_name="状态")
    entry_time = models.DateTimeField(verbose_name="入场时间")
    exit_time = models.DateTimeField(null=True, blank=True, verbose_name="离场时间")
    duration_minutes = models.IntegerField(default=0, verbose_name="停车时长（分钟）")
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="费用（元）")
    is_paid = models.BooleanField(default=False, verbose_name="是否已缴费")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "停车会话"
        verbose_name_plural = "停车会话"
        ordering = ["-id"]

    def __str__(self) -> str:
        return f"ParkingSession(id={self.id}, plate={self.license_plate}, status={self.status})"


class ViolationRecord(models.Model):
    """违规停车记录"""

    TYPE_FIRE_LANE = "fire_lane"
    TYPE_NO_PARKING = "no_parking"
    TYPE_DOUBLE_PARK = "double_park"
    TYPE_CHOICES = [
        (TYPE_FIRE_LANE, "占用消防通道"),
        (TYPE_NO_PARKING, "禁停区停车"),
        (TYPE_DOUBLE_PARK, "双排停车"),
    ]

    STATUS_PENDING = "pending"
    STATUS_RESOLVED = "resolved"
    STATUS_CHOICES = [
        (STATUS_PENDING, "待处理"),
        (STATUS_RESOLVED, "已处理"),
    ]

    lot = models.ForeignKey(
        ParkingLot,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="violations",
        verbose_name="停车场",
    )
    camera = models.ForeignKey(
        Camera,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="violations",
        verbose_name="触发摄像头",
    )
    track_id = models.IntegerField(null=True, blank=True, verbose_name="跟踪ID")
    license_plate = models.CharField(max_length=32, blank=True, default="", verbose_name="车牌号")
    violation_type = models.CharField(max_length=32, choices=TYPE_CHOICES, default=TYPE_FIRE_LANE, verbose_name="违规类型")
    zone_name = models.CharField(max_length=64, blank=True, default="", verbose_name="违规区域名称")
    duration_seconds = models.IntegerField(default=0, verbose_name="驻留秒数")
    snapshot = models.ImageField(upload_to="parking/violations/%Y/%m/%d/", null=True, blank=True, verbose_name="违规截图")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING, verbose_name="处理状态")
    remark = models.CharField(max_length=255, blank=True, default="", verbose_name="处理备注")
    violated_at = models.DateTimeField(verbose_name="违规时间")
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="处理时间")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "违规记录"
        verbose_name_plural = "违规记录"
        ordering = ["-id"]

    def __str__(self) -> str:
        return f"ViolationRecord(id={self.id}, type={self.violation_type}, status={self.status})"


class BillingRule(models.Model):
    """计费规则"""

    lot = models.ForeignKey(
        ParkingLot,
        on_delete=models.CASCADE,
        related_name="billing_rules",
        verbose_name="所属停车场",
    )
    vehicle_type = models.CharField(max_length=32, default="car", verbose_name="适用车型")
    free_minutes = models.IntegerField(default=15, verbose_name="免费时长（分钟）")
    rate_per_hour = models.DecimalField(max_digits=6, decimal_places=2, default=5.00, verbose_name="每小时费率（元）")
    daily_max = models.DecimalField(max_digits=8, decimal_places=2, default=50.00, verbose_name="日封顶费用（元）")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "计费规则"
        verbose_name_plural = "计费规则"
        ordering = ["lot", "vehicle_type"]

    def __str__(self) -> str:
        return f"BillingRule(lot={self.lot_id}, type={self.vehicle_type}, rate={self.rate_per_hour})"
