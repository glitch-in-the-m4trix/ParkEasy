from django import forms
from datetime import date
from .models import *


class BaseControlForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            if isinstance(field, (forms.FileField, forms.ImageField)):
                field.widget = forms.FileInput()
                field.widget.attrs.update({"title": field.label})

            if isinstance(field, forms.DateField):
                field.widget = forms.DateInput(attrs={"type": "date"})
                field.widget.attrs.update({"title": field.label})

            if isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs.update({"class": "form-check-input"})
                continue

            if isinstance(field, forms.ModelChoiceField):
                field.empty_label = f"Select {field.label}"

            field.widget.attrs.update({"class": "form-control"})


class LogDataForm(BaseControlForm):
    class Meta:
        model = LogData
        fields = ["username", "password"]

        widgets = {
            "password": forms.PasswordInput(),
        }


class ParkingRateForm(BaseControlForm):
    class Meta:
        model = ParkingRate
        fields = "__all__"


class DistrictAdminForm(BaseControlForm):
    class Meta:
        model = DistrictAdmin
        exclude = ["log_data"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        today = date.today()

        self.fields["dob"].widget.attrs["min"] = date(
            today.year - 60, today.month, today.day
        ).isoformat()

        self.fields["dob"].widget.attrs["max"] = date(
            today.year - 18, today.month, today.day
        ).isoformat()


class ParkingAreaForm(BaseControlForm):
    class Meta:
        model = ParkingArea
        exclude = ["district"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["longitude"].widget.attrs["readonly"] = True
        self.fields["latitude"].widget.attrs["readonly"] = True


class ParkingGridForm(BaseControlForm):
    class Meta:
        model = ParkingGrid
        exclude = ["parking_area", "vehicle_type"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["online_bookable"].widget.attrs.update({"min": 1, "max": 100})


class StreetForm(BaseControlForm):
    class Meta:
        model = Street
        fields = ["name"]


class StaffForm(BaseControlForm):
    class Meta:
        model = Staff
        exclude = ["log_data", "parking_area"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        today = date.today()

        self.fields["dob"].widget.attrs["min"] = date(
            today.year - 60, today.month, today.day
        ).isoformat()

        self.fields["dob"].widget.attrs["max"] = date(
            today.year - 18, today.month, today.day
        ).isoformat()


class StreetStaffForm(BaseControlForm):
    class Meta:
        model = StreetStaff
        exclude = ["log_data", "district"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        today = date.today()

        self.fields["dob"].widget.attrs["min"] = date(
            today.year - 60, today.month, today.day
        ).isoformat()

        self.fields["dob"].widget.attrs["max"] = date(
            today.year - 18, today.month, today.day
        ).isoformat()


class UserForm(BaseControlForm):
    class Meta:
        model = User
        exclude = ["log_data"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        today = date.today()

        self.fields["dob"].widget.attrs["min"] = date(
            today.year - 60, today.month, today.day
        ).isoformat()

        self.fields["dob"].widget.attrs["max"] = date(
            today.year - 18, today.month, today.day
        ).isoformat()


class BookingForm(BaseControlForm):
    class Meta:
        model = Booking
        fields = ["vehicle_no"]


class ParkingForm(BaseControlForm):
    class Meta:
        model = Parking
        fields = ["vehicle_no", "user"]


class ReviewForm(BaseControlForm):
    class Meta:
        model = Review
        exclude = ["parking_area", "user"]


class StreetParkingForm(BaseControlForm):
    class Meta:
        model = StreetParking
        fields = ["street", "vehicle_no", "vehicle_type"]

    def __init__(self, *args, **kwargs):
        district = kwargs.pop("district", None)
        super().__init__(*args, **kwargs)

        if district:
            self.fields["street"].queryset = Street.objects.filter(district=district)
