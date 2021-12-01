"""Asynchronous Python client providing RDW vehicle information."""

from enum import Enum


class Dataset(str, Enum):
    """Enum holding the RDW dataset identifiers for the Socrata API."""

    PLATED_VEHICLES = "m9d7-ebf2"


class VehicleType(str, Enum):
    """Enum holding the RDW vehicle types."""

    TAILER = "Aanhangwagen"
    PASSENGER_CAR = "Personenauto"
    COMPANY_CAR = "Bedrijfsauto"
    BUS = "Bus"
    MOTORCYCLE = "Motorfiets"
    THREE_WHEELED_MOTOR_VEHICLE = "Driewielig motorrijtuig"
    MOPED = "Bromfiets"
    CENTER_AXLE_TRAILER = "Middenasaanhangwagen"
    AGRICULTURAL_OR_FORESTRY_TRACTOR = "Land- of bosbouwtrekker"
    AGRICULTURAL_OR_FORESTRY_TRACTOR_TRAILER = "Land- of bosb aanhw of getr uitr stuk"


class VehicleInterior(str, Enum):
    """Enum holding the RDW vehicle interior types."""

    CAMPER = "kampeerwagen"
    CARAVAN = "caravan"
    CLOSED_INTERIOR = "closed_interior"
    CONVERTIBLE = "cabriolet"
    COUPE = "coupe"
    FIRETRUCK = "brandweerwagen"
    HATCHBACK = "hatchback"
    LIVESTOCK_TRUCK = "veewagen"
    MPV = "MPV"
    OPEN_LOADING_FLOOR = "open laadvloer"
    OPEN_VEHICLE = "open wagen"
    SEDAN = "sedan"
    STATION_WAGON = "stationwagen"
    PICK_UP_TRUCK = "pick-up truck"


class VehicleOdometerJudgement(str, Enum):
    """Enum holding the RDW vehicle odometer judgement types."""

    NO_JUDGEMENT = "Geen oordeel"
    LOGICAL = "Logisch"
    ILLOGICAL = "Onlogisch"
    UNKNOWN = "UNKNOWN"
