"""Asynchronous Python client providing RDW vehicle information."""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, validator

from .const import VehicleInterior, VehicleOdometerJudgement, VehicleType


class Vehicle(BaseModel):
    """Object holding vehicle information.

    Attributes:
        apk_expiration: Expiry date of the APK.
        brand: Brand of the vehicle.
        energy_label: Energy label of the vehicle.
        engine_capacity: Engine capacity of the vehicle in CC
        exported: Whether the vehicle is exported or not.
        first_admission_netherlands: First date of registration in the Netherlands.
        first_admission: First date of registration.
        interior: Interior of the vehicle.
        last_odometer_registration_year: Last year odometer was registered.
        liability_insured: Whether the vehicle is insured or not.
        license_plate: Normalized license plate of the vehicle.
        list_price: List price of the vehicle.
        mass_drivable: Mass of the vehicle when drivable in KG.
        mass_empty: Empty mass of the vehicle in KG.
        model: Model of the vehicle.
        name_registration_date: Date of naming registration of the vehicle.
        name_registration_possible: Whether the vehicle is nameable or not.
        number_of_cylinders: Number of cylinders of the vehicle.
        number_of_doors: Number of doors of the vehicle.
        number_of_seats: Number of seats of the vehicle.
        number_of_wheelchair_seats: Number of wheelchair seats of the vehicle.
        number_of_wheels: Number of wheels of the vehicle.
        odometer_judgement: Odometer judgement of the vehicle.
        pending_recall: Whether the vehicle has a pending recall or not.
        taxi: Whether the vehicle is a taxi or not.
        vehicle_type: Type of the vehicle.
    """

    apk_expiration: date = Field(..., alias="vervaldatum_apk")
    brand: str = Field(..., alias="merk")
    energy_label: Optional[str] = Field(None, alias="zuinigheidslabel")
    engine_capacity: Optional[int] = Field(None, alias="cilinderinhoud")
    exported: Optional[bool] = Field(None, alias="export_indicator")
    interior: Optional[VehicleInterior] = Field(None, alias="inrichting")
    last_odometer_registration_year: Optional[int] = Field(
        None, alias="jaar_laatste_registratie_tellerstand"
    )
    liability_insured: Optional[bool] = Field(None, alias="wam_verzekerd")
    license_plate: str = Field(..., alias="kenteken")
    list_price: Optional[int] = Field(None, alias="catalogusprijs")
    first_admission: date = Field(..., alias="datum_eerste_toelating")
    first_admission_netherlands: date = Field(
        ..., alias="datum_eerste_afgifte_nederland"
    )
    mass_empty: Optional[int] = Field(None, alias="massa_ledig_voertuig")
    mass_driveable: Optional[int] = Field(None, alias="massa_rijklaar")
    model: str = Field(..., alias="handelsbenaming")
    ascription_date: date = Field(..., alias="datum_tenaamstelling")
    ascription_possible: Optional[bool] = Field(None, alias="tenaamstellen_mogelijk")
    number_of_cylinders: Optional[int] = Field(None, alias="aantal_cilinders")
    number_of_doors: Optional[int] = Field(None, alias="aantal_deuren")
    number_of_seats: Optional[int] = Field(None, alias="aantal_zitplaatsen")
    number_of_wheelchair_seats: Optional[int] = Field(
        None, alias="aantal_rolstoelplaatsen"
    )
    number_of_wheels: Optional[int] = Field(None, alias="aantal_wielen")
    odometer_judgement: VehicleOdometerJudgement = Field(
        None, alias="tellerstandoordeel"
    )
    pending_recall: Optional[bool] = Field(
        None, alias="openstaande_terugroepactie_indicator"
    )
    taxi: Optional[bool] = Field(None, alias="taxi_indicator")
    vehicle_type: Optional[VehicleType] = Field(None, alias="voertuigsoort")

    @validator(
        "apk_expiration",
        "first_admission_netherlands",
        "first_admission",
        "name_registration_date",
        pre=True,
    )
    @classmethod
    def parse_date(cls, value: str) -> date:  # noqa: F841
        """Parse date from string.

        Args:
            value: String to parse.

        Returns:
            Parsed date.
        """
        return datetime.strptime(value, "%Y%m%d").date()

    @validator(
        "exported",
        "liability_insured",
        "name_registration_possible",
        "pending_recall",
        "taxi",
        pre=True,
    )
    @classmethod
    def parse_bool(cls, value: str) -> Optional[bool]:  # noqa: F841
        """Parse boolean from string.

        Args:
            value: String to parse.

        Returns:
            Parsed boolean.
        """
        return value == "Ja"

    @validator("brand", "model")
    @classmethod
    def make_pretty(cls, value: str) -> str:  # noqa: F841
        """Parse date from string.

        Args:
            value: String to make pretty.

        Returns:
            Pretty string.
        """
        return value.strip().title()

    @validator(
        "interior",
        "odometer_judgement",
        "vehicle_type",
        pre=True,
    )
    @classmethod
    def filter_empty(cls, value: str) -> Optional[str]:  # noqa: F841
        """Filter out empty values.

        Args:
            value: String to filter.

        Returns:
            Filtered string.
        """
        if value in {"Niet geregistreerd", "N.v.t."}:
            return None
        return value
