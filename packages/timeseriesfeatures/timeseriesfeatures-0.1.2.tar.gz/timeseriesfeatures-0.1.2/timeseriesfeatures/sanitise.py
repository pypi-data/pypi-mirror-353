"""Functions for sanitising strings."""

DT_SANITISATION_REPLACEMENTS = {
    ":": "_",
    "/": "-",
}


def sanitise_dt_isoformat(column: str) -> str:
    """Sanitise a datetime ISO format."""
    for k, v in DT_SANITISATION_REPLACEMENTS.items():
        column = column.replace(k, v)
    return column
