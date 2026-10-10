from __future__ import annotations
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager


class LogDataManager(BaseUserManager):
    def create_user(
        self, username: str, password: str, role: str, **extra_fields: object
    ) -> LogData:
        user = self.model(username=username, role=role, **extra_fields)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(
        self, username: str, password: str, **extra_fields: object
    ) -> LogData:
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(username, password, "admin", **extra_fields)


class LogData(AbstractUser):
    role = models.CharField(max_length=50)
    status = models.IntegerField(
        default=1, db_comment="0: Pending\n" "1: Approved\n" "2: Rejected\n"
    )

    objects = LogDataManager()
    REQUIRED_FIELDS = ["role"]

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    @property
    def is_district_admin(self) -> bool:
        return self.role == "district_admin"

    @property
    def is_staff(self) -> bool:
        return self.role == "staff"

    @property
    def is_street_staff(self) -> bool:
        return self.role == "street_staff"

    @property
    def is_user(self) -> bool:
        return self.role == "user"

    def __str__(self):
        return self.username


class State(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class District(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name="districts")
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class ParkingRate(models.Model):
    two_wheeler_rate = models.CharField(max_length=2)
    three_wheeler_rate = models.CharField(max_length=2)
    four_wheeler_rate = models.CharField(max_length=2)


class DistrictAdmin(models.Model):
    log_data = models.OneToOneField(
        LogData, on_delete=models.CASCADE, related_name="district_admin"
    )
    district = models.ForeignKey(
        District, on_delete=models.CASCADE, related_name="district_admins", unique=True
    )
    name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to="district_admins/")
    dob = models.DateField(verbose_name="Date of Birth")
    phone = models.CharField(max_length=15)
    address = models.TextField()

    def __str__(self):
        return self.name


class ParkingArea(models.Model):
    district = models.ForeignKey(
        District, on_delete=models.CASCADE, related_name="parking_areas"
    )
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.TextField()

    def __str__(self):
        return self.name


class ParkingGrid(models.Model):
    VEHICLE_TYPES = [
        ("2W", "Two-wheeler"),
        ("3W", "Three-wheeler"),
        ("4W", "Four-wheeler"),
    ]

    parking_area = models.ForeignKey(
        ParkingArea, on_delete=models.CASCADE, related_name="parking_grids"
    )
    vehicle_type = models.CharField(max_length=2, choices=VEHICLE_TYPES)
    rows = models.PositiveIntegerField()
    columns = models.PositiveIntegerField()
    online_bookable = models.PositiveIntegerField(
        verbose_name="Online Booking Percentage"
    )

    @property
    def online_bookable_slots(self) -> int:
        total_slots = self.rows * self.columns
        return total_slots * self.online_booking_percentage // 100

    def __str__(self):
        return f"{self.parking_area.name} - {self.vehicle_type}"


class ParkingSlot(models.Model):
    STATUS_CHOICES = [
        (0, "Available"),
        (1, "Booked"),
        (2, "Occupied"),
        (3, "Maintenance"),
    ]

    parking_grid = models.ForeignKey(
        ParkingGrid, on_delete=models.CASCADE, related_name="parking_slots"
    )
    slot = models.CharField(max_length=10)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["parking_grid", "slot"],
                name="unique_slot_per_grid",
            )
        ]

    def __str__(self):
        return (
            f"{self.parking_grid.parking_area.name} "
            f"{self.parking_grid.vehicle_type} - {self.slot}"
        )


class Staff(models.Model):
    log_data = models.OneToOneField(
        LogData, on_delete=models.CASCADE, related_name="staff"
    )
    parking_area = models.ForeignKey(
        ParkingArea, on_delete=models.CASCADE, related_name="staff"
    )
    name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to="staff/")
    dob = models.DateField(verbose_name="Date of Birth")
    phone = models.CharField(max_length=15)
    address = models.TextField()

    def __str__(self):
        return self.name


class Street(models.Model):
    district = models.ForeignKey(
        District, on_delete=models.CASCADE, related_name="streets", blank=True
    )
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class StreetStaff(models.Model):
    log_data = models.OneToOneField(
        LogData, on_delete=models.CASCADE, related_name="street_staff"
    )
    district = models.ForeignKey(
        District, on_delete=models.CASCADE, related_name="street_staff"
    )
    name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to="staff/")
    dob = models.DateField(verbose_name="Date of Birth")
    phone = models.CharField(max_length=15)
    address = models.TextField()

    def __str__(self):
        return self.name


class User(models.Model):
    log_data = models.OneToOneField(
        LogData, on_delete=models.CASCADE, related_name="user"
    )
    name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to="users/")
    dob = models.DateField(verbose_name="Date of Birth")
    phone = models.CharField(max_length=15)
    address = models.TextField()

    def __str__(self):
        return self.name


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    parking_slot = models.ForeignKey(
        ParkingSlot, on_delete=models.CASCADE, related_name="bookings"
    )
    vehicle_no = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.PositiveSmallIntegerField(
        default=0, db_comment="0: Booked\n" "1: Parked\n" "2: Left\n" "3: Expired\n"
    )

    def __str__(self):
        return f"{self.user.name} - {self.parking_slot}"


class Parking(models.Model):
    parking_slot = models.ForeignKey(
        ParkingSlot, on_delete=models.CASCADE, related_name="parkings"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="parkings", null=True, blank=True
    )
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="parkings",
        null=True,
        blank=True,
    )
    vehicle_no = models.CharField(max_length=20)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    type = models.PositiveSmallIntegerField(
        default=1, db_comment="1: Drive-In\n" "2: Booked Online\n"
    )
    status = models.PositiveSmallIntegerField(
        default=1, db_comment="1: Parked\n" "2: Left\n"
    )

    def __str__(self):
        return f"{self.user.name} - {self.parking_slot}"


class Payment(models.Model):
    parking = models.OneToOneField(
        Parking, on_delete=models.CASCADE, related_name="payment"
    )
    amount = models.IntegerField()

    def __str__(self):
        return f"{self.parking.user.name} - {self.parking.parking_slot}"


class StreetParking(models.Model):
    VEHICLE_TYPES = [
        ("", "Select Vehicle Type"),
        ("2W", "Two-wheeler"),
        ("3W", "Three-wheeler"),
        ("4W", "Four-wheeler"),
    ]
    
    street = models.ForeignKey(
        Street, on_delete=models.CASCADE, related_name="street_parkings"
    )
    vehicle_no = models.CharField(max_length=20)
    vehicle_type = models.CharField(max_length=2, choices=VEHICLE_TYPES)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.PositiveSmallIntegerField(
        default=1, db_comment="1: Parked\n" "2: Left\n"
    )

    def __str__(self):
        return f"{self.vehicle_no} - {self.street}"


class StreetPayment(models.Model):
    street_parking = models.OneToOneField(
        StreetParking, on_delete=models.CASCADE, related_name="street_payment"
    )
    amount = models.IntegerField()

    def __str__(self):
        return f"{self.street_parking.vehicle_no} - {self.street_parking.street}"


class StreetPayment(models.Model):
    street_parking = models.ForeignKey(
        StreetParking, on_delete=models.CASCADE, related_name="street_payments"
    )
    amount = models.IntegerField()

    def __str__(self):
        return f"{self.street_parking.vehicle_no} - {self.street_parking.street}"


class Review(models.Model):
    parking_area = models.ForeignKey(
        ParkingArea, on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=100)
    review = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
