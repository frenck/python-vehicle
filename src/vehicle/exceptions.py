"""Asynchronous Python client providing RDW vehicle information."""


class RDWError(Exception):
    """Generic exception."""


class RDWUnknownLicensePlateError(RDWError):
    """RDW connection exception."""


class RDWConnectionError(RDWError):
    """RDW connection exception."""
