"""
seed_demo.py - Quick demo data generator for Windows (ASCII version)
Usage: python seed_demo.py
"""
import os, sys, django, secrets

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_main.settings")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from parking.models import ParkingLot, ParkingSpace, Camera, VehicleRecord, ParkingSession, ViolationRecord, BillingRule
import random
from decimal import Decimal
from datetime import datetime, timedelta

User = get_user_model()

# Create Admin
admin_password = os.environ.get("DEMO_ADMIN_PASSWORD")
if not User.objects.filter(username='admin').exists():
    if not admin_password:
        admin_password = secrets.token_urlsafe(12)
    User.objects.create_superuser('admin', '', admin_password)
    print('OK: Superuser admin created')
    print(f'Admin: admin / {admin_password}')
else:
    print('OK: Superuser already exists')

# Parking Lot
lot, _ = ParkingLot.objects.get_or_create(
    name='Demo Parking Lot A',
    defaults=dict(address='Beijing Road No.1', total_spaces=20, description='Demo lot')
)
print(f'OK: Parking Lot created: {lot.name}')

# Camera
cam, _ = Camera.objects.get_or_create(
    lot=lot, name='Entrance Cam A',
    defaults=dict(stream_url='rtsp://demo/stream1', status='online',
                  alert_zones=[{"name":"Fire Lane","coords":[[0,0],[100,0],[100,50],[0,50]],"threshold_sec":30}])
)

# Billing Rules
for vtype, rate, daily in [('car',5,50),('truck',10,100),('motorcycle',2,20)]:
    BillingRule.objects.get_or_create(lot=lot, vehicle_type=vtype,
        defaults=dict(free_minutes=15, rate_per_hour=Decimal(str(rate)), daily_max=Decimal(str(daily))))

# Spaces
types = ['small']*15 + ['large']*3 + ['disabled_person']*2
statuses = ['available']*12 + ['occupied']*6 + ['disabled']*2
for i in range(1, 21):
    ParkingSpace.objects.get_or_create(
        lot=lot, space_no=f'A-{i:02d}',
        defaults=dict(
            space_type=types[i-1],
            status=statuses[i-1],
            coordinates=[[50+(i-1)%5*110, 30+(i-1)//5*130],
                         [140+(i-1)%5*110, 30+(i-1)//5*130],
                         [140+(i-1)%5*110, 130+(i-1)//5*130],
                         [50+(i-1)%5*110, 130+(i-1)//5*130]],
            camera=cam,
        )
    )

# Vehicle records (Past 7 days)
plates = ['ABC-123', 'DEF-456', 'GHI-789', 'JKL-012', 'MNO-345']
vtypes = ['car','car','car','truck','motorcycle']
now = timezone.now()
for day_offset in range(7):
    day = now - timedelta(days=day_offset)
    for _ in range(random.randint(5, 15)):
        plate = random.choice(plates)
        vtype = random.choice(vtypes)
        entry_t = day - timedelta(hours=random.randint(0,20))
        exit_t = entry_t + timedelta(minutes=random.randint(30, 180))
        if exit_t > now: continue
        
        duration = int((exit_t - entry_t).total_seconds() / 60)
        e_rec = VehicleRecord.objects.create(lot=lot, camera=cam, license_plate=plate, vehicle_type=vtype, direction='entry', recorded_at=entry_t)
        ex_rec = VehicleRecord.objects.create(lot=lot, camera=cam, license_plate=plate, vehicle_type=vtype, direction='exit', recorded_at=exit_t)
        
        fee = Decimal(str(round(max(0, (duration-15)/60)*5, 2)))
        ParkingSession.objects.create(lot=lot, license_plate=plate, vehicle_type=vtype, status='completed', entry_time=entry_t, exit_time=exit_t, duration_minutes=duration, fee=fee, is_paid=True)

# Active sessions
for i in range(3):
    entry_t = now - timedelta(minutes=random.randint(10, 90))
    entry_rec = VehicleRecord.objects.create(lot=lot, camera=cam, license_plate=plates[i], vehicle_type='car', direction='entry', recorded_at=entry_t)
    ParkingSession.objects.create(lot=lot, license_plate=plates[i], vehicle_type='car', status='active', entry_record=entry_rec, entry_time=entry_t)

# Violations
for i in range(3):
    ViolationRecord.objects.create(lot=lot, camera=cam, track_id=200+i, violation_type='fire_lane', zone_name='Fire Lane', duration_seconds=random.randint(40,120), status='pending', violated_at=now - timedelta(hours=i))

print('OK: Demo data generated successfully.')
print('Visit: http://127.0.0.1:8000 (Backend) / http://localhost:5173 (Frontend)')
