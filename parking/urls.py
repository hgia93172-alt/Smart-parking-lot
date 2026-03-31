from django.urls import path

from parking.views import (
    BillingRuleDetailView,
    BillingRuleListView,
    CameraDetailView,
    CameraListView,
    LotDashboardView,
    ParkingLotDetailView,
    ParkingLotListView,
    ParkingSessionDetailView,
    ParkingSessionListView,
    ParkingSpaceDetailView,
    ParkingSpaceListView,
    ParkingSpaceStatusView,
    StatsHourlyView,
    StatsOverviewView,
    StatsRevenueView,
    VehicleEntryView,
    VehicleExitView,
    VehicleRecordListView,
    ViolationRecordListView,
    ViolationResolveView,
)

urlpatterns = [
    # 停车场
    path("lots/", ParkingLotListView.as_view()),
    path("lots/<int:lot_id>/", ParkingLotDetailView.as_view()),
    path("lots/<int:lot_id>/dashboard/", LotDashboardView.as_view()),

    # 摄像头
    path("cameras/", CameraListView.as_view()),
    path("cameras/<int:cam_id>/", CameraDetailView.as_view()),

    # 车位
    path("spaces/", ParkingSpaceListView.as_view()),
    path("spaces/<int:space_id>/", ParkingSpaceDetailView.as_view()),
    path("spaces/<int:space_id>/status/", ParkingSpaceStatusView.as_view()),

    # 车辆进出记录
    path("vehicles/", VehicleRecordListView.as_view()),
    path("vehicles/entry/", VehicleEntryView.as_view()),
    path("vehicles/exit/", VehicleExitView.as_view()),

    # 停车会话
    path("sessions/", ParkingSessionListView.as_view()),
    path("sessions/<int:session_id>/", ParkingSessionDetailView.as_view()),

    # 违规记录
    path("violations/", ViolationRecordListView.as_view()),
    path("violations/<int:violation_id>/resolve/", ViolationResolveView.as_view()),

    # 计费规则
    path("billing-rules/", BillingRuleListView.as_view()),
    path("billing-rules/<int:rule_id>/", BillingRuleDetailView.as_view()),

    # 统计
    path("stats/overview/", StatsOverviewView.as_view()),
    path("stats/hourly/", StatsHourlyView.as_view()),
    path("stats/revenue/", StatsRevenueView.as_view()),
]
