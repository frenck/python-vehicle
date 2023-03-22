# pylint: disable=W0621
"""Asynchronous Python client providing RDW vehicle information."""

import asyncio

from vehicle import RDW, Vehicle


async def main() -> None:
    """Show example of fetching RDW vehicle info from Socrata API."""
    async with RDW() as rdw:
        vehicle: Vehicle = await rdw.vehicle(license_plate="AR6458")
        print(vehicle)


if __name__ == "__main__":
    asyncio.run(main())
