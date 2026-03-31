"""
parking_ai/billing.py
阶梯计费计算器（纯本地计算，仅供参考；最终收费由 Django 后端的 _calculate_fee 决定）。
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class BillingRule:
    vehicle_type: str = "car"
    free_minutes: int = 15          # 免费时长
    rate_per_hour: Decimal = Decimal("5.00")  # 每小时收费
    daily_max: Decimal = Decimal("50.00")     # 日封顶


DEFAULT_RULES: dict[str, BillingRule] = {
    "car": BillingRule("car", 15, Decimal("5.00"), Decimal("50.00")),
    "truck": BillingRule("truck", 10, Decimal("10.00"), Decimal("100.00")),
    "bus": BillingRule("bus", 10, Decimal("10.00"), Decimal("100.00")),
    "motorcycle": BillingRule("motorcycle", 30, Decimal("2.00"), Decimal("20.00")),
}


def calculate_fee(vehicle_type: str, duration_minutes: int, rule: BillingRule | None = None) -> Decimal:
    """根据车型和停车时长计算费用。"""
    if rule is None:
        rule = DEFAULT_RULES.get(vehicle_type, DEFAULT_RULES["car"])

    billable = max(0, duration_minutes - rule.free_minutes)
    hours = math.ceil(billable / 60)
    fee = Decimal(str(hours)) * rule.rate_per_hour
    return min(fee, rule.daily_max)


def format_duration(minutes: int) -> str:
    """将分钟数格式化为可读字符串。"""
    h = minutes // 60
    m = minutes % 60
    if h > 0:
        return f"{h}小时{m}分钟"
    return f"{m}分钟"
