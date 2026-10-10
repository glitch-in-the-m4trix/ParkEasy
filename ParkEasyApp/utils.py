from math import radians, sin, cos, sqrt, atan2                             
from .models import ParkingSlot


def get_row_label(row_num):
    label = ""

    while row_num > 0:
        row_num -= 1
        label = chr(65 + row_num % 26) + label
        row_num //= 26

    return label


def create_parking_slots(parking_grid):
    slots = []

    for row in range(1, parking_grid.rows + 1):
        row_label = get_row_label(row)

        for col in range(1, parking_grid.columns + 1):
            slot_label = f"{row_label}-{col}"

            slots.append(
                ParkingSlot(parking_grid=parking_grid, slot=slot_label, status=0)
            )

    ParkingSlot.objects.bulk_create(slots)


def row_number(label):
    number = 0
    for char in label:
        number = number * 26 + (ord(char) - ord("A") + 1)
    return number


def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c