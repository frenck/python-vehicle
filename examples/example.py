# pylint: disable=redefined-outer-name
"""Asynchronous Python client providing RDW vehicle information."""

import asyncio

from vehicle import RDW, Vehicle


async def main() -> None:
    """Show example of fetching RDW vehicle info from Socrata API."""
    async with RDW() as rdw:
        # Vehicle information
        vehicle: Vehicle = await rdw.vehicle(license_plate="11ZKZ3")
        print(vehicle)

        # Fuel and emission data
        fuels = await rdw.fuel(license_plate="11ZKZ3")
        for fuel in fuels:
            print(fuel)

        # Recall status
        recalls = await rdw.recalls(license_plate="11ZKZ3")
        for recall in recalls:
            print(recall)


if __name__ == "__main__":
    asyncio.run(main())
