"""Asynchronous Python client providing RDW vehicle information."""


class RDWError(Exception):
    """Generic exception."""


class RDWUnknownLicensePlateError(RDWError):
    """RDW unknown license plate exception."""


class RDWConnectionError(RDWError):
    """RDW connection exception."""
