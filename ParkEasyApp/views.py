from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import *
from .utils import *
from .forms import *
import math


def home(request: HttpRequest) -> HttpResponse:
    return render(request, "Common/Home.html")


def parking_rate(request: HttpRequest) -> HttpResponse:
    instance = ParkingRate.objects.first()
    form = ParkingRateForm(request.POST or None, instance=instance)

    if form.is_valid():
        form.save()

        messages.success(request, "Parking rate set successfully.")
        return redirect("ParkEasyApp:parking_rate")

    return render(request, "Admin/ParkingRate.html", {"form": form})


@transaction.atomic
def add_district_admin(request: HttpRequest) -> HttpResponse:
    log_form = LogDataForm(request.POST or None)
    district_admin_form = DistrictAdminForm(request.POST or None, request.FILES or None)

    states = State.objects.all()

    if log_form.is_valid() and district_admin_form.is_valid():
        log_data = log_form.save(commit=False)
        log_data.set_password(log_form.cleaned_data["password"])
        log_data.role = "district_admin"
        log_data.save()

        district_admin = district_admin_form.save(commit=False)
        district_admin.log_data = log_data
        district_admin.save()

        messages.success(request, "District Admin added successfully.")
        return redirect("ParkEasyApp:add_district_admin")

    return render(
        request,
        "Admin/AddDistrictAdmin.html",
        {
            "log_form": log_form,
            "district_admin_form": district_admin_form,
            "states": states,
        },
    )


def filter_districts(request) -> JsonResponse:
    state_id = request.GET.get("state")
    districts = District.objects.filter(state_id=state_id).values("id", "name")

    return JsonResponse({"districts": list(districts)})


@transaction.atomic
def add_parking_area(request: HttpRequest) -> HttpResponse:
    parking_area_form = ParkingAreaForm(request.POST or None)
    two_wheeler_grid_form = ParkingGridForm(request.POST or None, prefix="two_wheeler")
    three_wheeler_grid_form = ParkingGridForm(
        request.POST or None, prefix="three_wheeler"
    )
    four_wheeler_grid_form = ParkingGridForm(
        request.POST or None, prefix="four_wheeler"
    )

    if (
        parking_area_form.is_valid()
        and two_wheeler_grid_form.is_valid()
        and three_wheeler_grid_form.is_valid()
        and four_wheeler_grid_form.is_valid()
    ):
        parking_area = parking_area_form.save(commit=False)
        parking_area.district = request.user.district_admin.district
        parking_area.save()

        two_wheeler_grid = two_wheeler_grid_form.save(commit=False)
        two_wheeler_grid.parking_area = parking_area
        two_wheeler_grid.vehicle_type = "2W"
        two_wheeler_grid.save()
        create_parking_slots(two_wheeler_grid)

        three_wheeler_grid = three_wheeler_grid_form.save(commit=False)
        three_wheeler_grid.parking_area = parking_area
        three_wheeler_grid.vehicle_type = "3W"
        three_wheeler_grid.save()
        create_parking_slots(three_wheeler_grid)

        four_wheeler_grid = four_wheeler_grid_form.save(commit=False)
        four_wheeler_grid.parking_area = parking_area
        four_wheeler_grid.vehicle_type = "4W"
        four_wheeler_grid.save()
        create_parking_slots(four_wheeler_grid)

        messages.success(request, "Parking area added successfully.")
        return redirect("ParkEasyApp:add_parking_area")

    return render(
        request,
        "DistrictAdmin/AddParkingArea.html",
        {
            "parking_area_form": parking_area_form,
            "two_wheeler_grid_form": two_wheeler_grid_form,
            "three_wheeler_grid_form": three_wheeler_grid_form,
            "four_wheeler_grid_form": four_wheeler_grid_form,
        },
    )


def view_parking_areas(request: HttpRequest) -> HttpResponse:
    parking_areas = (
        ParkingArea.objects.filter(district=request.user.district_admin.district)
        if request.user.role == "district_admin"
        else ParkingArea.objects.all()
    )
    parking_areas = (
        parking_areas.annotate(
            two_wheeler_slots=Count(
                "parking_grids__parking_slots",
                filter=Q(parking_grids__vehicle_type="2W"),
            )
        )
        .annotate(
            three_wheeler_slots=Count(
                "parking_grids__parking_slots",
                filter=Q(parking_grids__vehicle_type="3W"),
            )
        )
        .annotate(
            four_wheeler_slots=Count(
                "parking_grids__parking_slots",
                filter=Q(parking_grids__vehicle_type="4W"),
            )
        )
        .order_by("name")
    )

    return render(
        request, "Common/ViewParkingAreas.html", {"parking_areas": parking_areas}
    )


def add_staff(request: HttpRequest, parking_area_id: int) -> HttpResponse:
    log_form = LogDataForm(request.POST or None)
    staff_form = StaffForm(request.POST or None, request.FILES or None)

    if log_form.is_valid() and staff_form.is_valid():
        log_data = log_form.save(commit=False)
        log_data.set_password(log_form.cleaned_data["password"])
        log_data.role = "staff"
        log_data.save()

        staff = staff_form.save(commit=False)
        staff.log_data = log_data
        staff.parking_area_id = parking_area_id
        staff.save()

        messages.success(request, "Staff added successfully.")
        return redirect("ParkEasyApp:add_staff", parking_area_id)

    return render(
        request,
        "DistrictAdmin/AddStaff.html",
        {"log_form": log_form, "staff_form": staff_form},
    )


def add_street(request: HttpRequest) -> HttpResponse:
    form = StreetForm(request.POST or None)

    if form.is_valid():
        street = form.save(commit=False)
        street.district = request.user.district_admin.district
        street.save()

        messages.success(request, "Street added successfully.")
        return redirect("ParkEasyApp:add_street")

    return render(request, "DistrictAdmin/AddStreet.html", {"form": form})


def add_street_staff(request: HttpRequest) -> HttpResponse:
    log_form = LogDataForm(request.POST or None)
    street_staff_form = StreetStaffForm(request.POST or None, request.FILES or None)

    if log_form.is_valid() and street_staff_form.is_valid():
        log_data = log_form.save(commit=False)
        log_data.set_password(log_form.cleaned_data["password"])
        log_data.role = "street_staff"
        log_data.save()

        street_staff = street_staff_form.save(commit=False)
        street_staff.log_data = log_data
        street_staff.district = request.user.district_admin.district
        street_staff.save()

        messages.success(request, "Street Staff added successfully.")
        return redirect("ParkEasyApp:add_street_staff")

    return render(
        request,
        "DistrictAdmin/AddStreetStaff.html",
        {"log_form": log_form, "street_staff_form": street_staff_form},
    )


@transaction.atomic
def view_slots(
    request: HttpRequest, vehicle_type: str, parking_area_id: int = None
) -> HttpResponse:
    parking_area_id = parking_area_id or request.user.staff.parking_area.id
    parking_grid = ParkingGrid.objects.get(
        parking_area_id=parking_area_id,
        vehicle_type=vehicle_type,
    )

    cutoff = timezone.now() - timedelta(minutes=10)
    expired_bookings = Booking.objects.filter(
        status=0,
        parking_slot__in=parking_grid.parking_slots.all(),
        created_at__lt=cutoff,
    )

    expired_slot_ids = list(expired_bookings.values_list("parking_slot_id", flat=True))
    expired_bookings.update(status=3)
    ParkingSlot.objects.filter(id__in=expired_slot_ids, status=1).update(status=0)

    slots = sorted(
        parking_grid.parking_slots.all(),
        key=lambda slot: (
            row_number(slot.slot.split("-")[0]),
            int(slot.slot.split("-")[1]),
        ),
    )

    return render(
        request,
        "Common/ViewSlots.html",
        {
            "parking_grid": parking_grid,
            "slots": slots,
        },
    )


def register(request: HttpRequest) -> HttpResponse:
    log_form = LogDataForm(request.POST or None)
    user_form = UserForm(request.POST or None, request.FILES or None)

    if log_form.is_valid() and user_form.is_valid():
        log_data = log_form.save(commit=False)
        log_data.set_password(log_form.cleaned_data["password"])
        log_data.role = "user"
        log_data.save()

        user = user_form.save(commit=False)
        user.log_data = log_data
        user.save()

        messages.success(request, "User registered successfully.")
        return redirect("ParkEasyApp:register")

    return render(
        request, "User/Register.html", {"log_form": log_form, "user_form": user_form}
    )


def nearby_parking(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        user_latitude = float(request.POST.get("latitude") or 0)
        user_longitude = float(request.POST.get("longitude") or 0)

        if not user_latitude or not user_longitude:
            messages.error(request, "Please enter a valid latitude and longitude.")
            return redirect("ParkEasyApp:nearby_parking")

        parking_areas = (
            ParkingArea.objects.all()
            .annotate(
                two_wheeler_slots=Count(
                    "parking_grids__parking_slots",
                    filter=Q(parking_grids__vehicle_type="2W"),
                )
            )
            .annotate(
                three_wheeler_slots=Count(
                    "parking_grids__parking_slots",
                    filter=Q(parking_grids__vehicle_type="3W"),
                )
            )
            .annotate(
                four_wheeler_slots=Count(
                    "parking_grids__parking_slots",
                    filter=Q(parking_grids__vehicle_type="4W"),
                )
            )
        )

        nearby_areas = []

        for area in parking_areas:
            distance = calculate_distance(
                user_latitude,
                user_longitude,
                area.latitude,
                area.longitude,
            )

            if distance <= 5:
                area.distance = round(distance, 2)
                nearby_areas.append(area)

        nearby_areas.sort(key=lambda area: area.distance)

        return render(
            request,
            "Common/ViewParkingAreas.html",
            {"parking_areas": nearby_areas},
        )

    return render(request, "User/NearbyParkingAreas.html")


@transaction.atomic
def book_slot(request: HttpRequest, slot_id: int) -> HttpResponse:
    form = BookingForm(request.POST or None)

    if form.is_valid():
        parking_slot = ParkingSlot.objects.get(id=slot_id)
        parking_slot.status = 1
        parking_slot.save()

        booking = form.save(commit=False)
        booking.user = request.user.user
        booking.parking_slot = parking_slot
        booking.save()

        messages.success(request, "Slot booked successfully.")
        return redirect("ParkEasyApp:nearby_parking")

    return render(request, "User/BookSlot.html", {"form": form})


@transaction.atomic
def update_slot(request: HttpRequest, slot_id: int, status: int) -> HttpResponse:
    slot = ParkingSlot.objects.get(id=slot_id)

    if status == 0:
        form = ParkingForm(request.POST or None)
    elif status == 1:
        booking = Booking.objects.get(parking_slot=slot, status=0)
        form = ParkingForm(
            request.POST or None,
            initial={"user": booking.user, "vehicle_no": booking.vehicle_no},
        )
    elif status == 2:
        return redirect("ParkEasyApp:payment", slot_id)

    if form.is_valid():
        slot.status = 2
        slot.save()

        if status == 0:
            parking = form.save(commit=False)
            parking.type = 1
            parking.parking_slot = slot
            parking.save()

        elif status == 1:
            parking = form.save(commit=False)
            parking.booking = booking
            parking.type = 2
            parking.parking_slot = slot
            parking.save()

            booking.status = 1
            booking.save()

        messages.success(request, "Slot updated successfully.")
        return redirect("ParkEasyApp:view_slots", slot.parking_grid.vehicle_type)

    return render(request, "Staff/EntryForm.html", {"form": form})


def payment(request: HttpRequest, slot_id: int) -> HttpResponse:
    parking = Parking.objects.get(parking_slot_id=slot_id, status=1)
    vehicle_type = parking.parking_slot.parking_grid.vehicle_type
    parking_rate = ParkingRate.objects.first()
    end_time = timezone.now()
    duration = end_time - parking.start_time
    hours = math.ceil(duration.total_seconds() / 3600)

    rate = {
        "2W": parking_rate.two_wheeler_rate,
        "3W": parking_rate.three_wheeler_rate,
        "4W": parking_rate.four_wheeler_rate,
    }[vehicle_type]
    amount = hours * int(rate)

    if request.method == "POST":
        Payment.objects.create(parking=parking, amount=amount)

        parking.end_time = end_time
        parking.status = 2
        parking.save()

        if parking.type == 2:
            booking = parking.booking
            booking.status = 2
            booking.save()

        parking_slot = parking.parking_slot
        parking_slot.status = 0
        parking_slot.save()

        messages.success(request, "Payment submitted successfully.")
        return redirect("ParkEasyApp:view_slots", vehicle_type)

    return render(
        request,
        "Staff/Payment.html",
        {
            "parking": parking,
            "rate": rate,
            "end_time": end_time,
            "hours": hours,
            "amount": amount,
        },
    )


def payments(request: HttpRequest, parking_area_id: int) -> HttpResponse:
    payments = Payment.objects.filter(
        parking__parking_slot__parking_grid__parking_area=parking_area_id
    ).order_by("-id")

    for payment in payments:
        duration = payment.parking.end_time - payment.parking.start_time
        hours = math.ceil(duration.total_seconds() / 3600)
        payment.fee = hours * int(payment.amount)

    return render(request, "DistrictAdmin/Payments.html", {"payments": payments})


def search_vehicle(request: HttpRequest, parked=False) -> HttpResponse:
    parking_history = None

    if request.method == "POST":
        vehicle_no = request.POST["vehicle_no"]

        if parked:
            parking = Parking.objects.filter(vehicle_no=vehicle_no, status=1)

            if not parking.exists():
                messages.error(request, "Vehicle not found.")
                return redirect(
                    "ParkEasyApp:search_vehicle", {"parking_history": parking_history}
                )

            parking_slot = parking[0].parking_slot
            parking_grid = parking_slot.parking_grid

            slots = sorted(
                parking_grid.parking_slots.all(),
                key=lambda slot: (
                    row_number(slot.slot.split("-")[0]),
                    int(slot.slot.split("-")[1]),
                ),
            )

            return render(
                request,
                "Staff/ParkedVehicle.html",
                {
                    "parking_slot": parking_slot,
                    "slots": slots,
                    "parking_grid": parking_grid,
                },
            )

        else:
            parking_history = Parking.objects.filter(vehicle_no=vehicle_no)

    return render(
        request, "Admin/ParkingHistory.html", {"parking_history": parking_history}
    )


def slot_history(request: HttpRequest, slot_id: int) -> HttpResponse:
    parking_history = Parking.objects.filter(parking_slot_id=slot_id)
    return render(
        request, "Admin/ParkingHistory.html", {"parking_history": parking_history}
    )


def reviews(request: HttpRequest, parking_area_id: int) -> HttpResponse:
    form = ReviewForm(request.POST or None)

    if form.is_valid():
        if not form.cleaned_data["rating"]:
            messages.error(request, "Please select a rating.")
        else:
            review = form.save(commit=False)
            review.parking_area_id = parking_area_id
            review.user = request.user.user
            review.save()

            messages.success(request, "Review submitted successfully.")
            return redirect("ParkEasyApp:reviews", parking_area_id)

    reviews = Review.objects.filter(parking_area_id=parking_area_id)
    return render(request, "Common/Reviews.html", {"form": form, "reviews": reviews})


def add_street_parking(request: HttpRequest) -> HttpResponse:
    form = StreetParkingForm(
        request.POST or None, district=request.user.street_staff.district
    )

    if form.is_valid():
        form.save()

        messages.success(request, "Street parking added successfully.")
        return redirect("ParkEasyApp:add_street_parking")

    return render(request, "StreetStaff/AddStreetParking.html", {"form": form})


def view_street_parking(request: HttpRequest) -> HttpResponse:
    streets = Street.objects.filter(district=request.user.street_staff.district)
    street_parkings = end_time = None

    if request.method == "POST":
        street_id = request.POST["street"]
        street_parkings = StreetParking.objects.filter(street_id=street_id, status=1)

        for street_parking in street_parkings:
            end_time = street_parking.end_time or timezone.now()
            duration = end_time - street_parking.start_time
            hours = math.ceil(duration.total_seconds() / 3600)
            vehicle_type = street_parking.vehicle_type
            parking_rate = ParkingRate.objects.first()
            rate = {
                "2W": parking_rate.two_wheeler_rate,
                "3W": parking_rate.three_wheeler_rate,
                "4W": parking_rate.four_wheeler_rate,
            }[vehicle_type]
            street_parking.fee = hours * rate

    return render(
        request,
        "StreetStaff/ViewStreetParking.html",
        {"streets": streets, "street_parkings": street_parkings, "end_time": end_time},
    )


def street_payment(request: HttpRequest, street_parking_id: int) -> HttpResponse:
    street_parking = StreetParking.objects.get(id=street_parking_id)

    end_time = timezone.now()
    duration = end_time - street_parking.start_time
    hours = math.ceil(duration.total_seconds() / 3600)
    vehicle_type = street_parking.vehicle_type
    parking_rate = ParkingRate.objects.first()
    rate = {
        "2W": parking_rate.two_wheeler_rate,
        "3W": parking_rate.three_wheeler_rate,
        "4W": parking_rate.four_wheeler_rate,
    }[vehicle_type]
    amount = hours * rate

    StreetPayment.objects.create(street_parking=street_parking, amount=amount)
    street_parking.end_time = end_time
    street_parking.status = 2
    street_parking.save()

    messages.success(request, "Payment made successfully.")
    return redirect(request.META.get("HTTP_REFERER"))
