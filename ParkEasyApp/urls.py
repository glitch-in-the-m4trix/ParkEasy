from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

app_name = "ParkEasyApp"

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", LoginView.as_view(template_name="Common/Login.html"), name="login"),
    path("parking-rate/", views.parking_rate, name="parking_rate"),
    path("add-district-admin/", views.add_district_admin, name="add_district_admin"),
    path("filter-districts/", views.filter_districts, name="filter_districts"),
    path("add-parking-area/", views.add_parking_area, name="add_parking_area"),
    path("view-parking-areas/", views.view_parking_areas, name="view_parking_areas"),
    path("add-staff/<int:parking_area_id>/", views.add_staff, name="add_staff"),
    path("add-street/", views.add_street, name="add_street"),
    path("add-street-staff/", views.add_street_staff, name="add_street_staff"),
    path("view-slots/<str:vehicle_type>/", views.view_slots, name="view_slots"),
    path(
        "view-slots/<str:vehicle_type>/<int:parking_area_id>/",
        views.view_slots,
        name="view_slots",
    ),
    path("register/", views.register, name="register"),
    path("nearby-parking/", views.nearby_parking, name="nearby_parking"),
    path("book-slot/<int:slot_id>/", views.book_slot, name="book_slot"),
    path("update-slot/<int:slot_id>/<int:status>/", views.update_slot, name="update_slot"),
    path("payment/<int:slot_id>/", views.payment, name="payment"),
    path("payments/<int:parking_area_id>/", views.payments, name="payments"),
    path("search-vehicle/", views.search_vehicle, name="search_vehicle"),
    path("search-vehicle/<str:parked>/", views.search_vehicle, name="search_vehicle"),
    path("slot-history/<int:slot_id>/", views.slot_history, name="slot_history"),
    path("reviews/<int:parking_area_id>/", views.reviews, name="reviews"),
    path("add-street-parking", views.add_street_parking, name="add_street_parking"),
    path("view-street-parking", views.view_street_parking, name="view_street_parking"),
    path("street_payment/<int:street_parking_id>/", views.street_payment, name="street_payment"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
