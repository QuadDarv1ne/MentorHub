"""
Pagination validation utilities
Common helpers for skip/limit validation to avoid code duplication
"""



def validate_pagination(skip: int, limit: int, max_limit: int = 100) -> tuple[int, int]:
    """
    Validate and normalize pagination parameters.

    Args:
        skip: Number of records to skip (must be >= 0)
        limit: Number of records to return (must be 1-max_limit)
        max_limit: Maximum allowed limit (default 100)

    Returns:
        Tuple of (validated_skip, validated_limit)
    """
    if skip < 0:
        skip = 0
    if limit <= 0 or limit > max_limit:
        limit = max_limit

    return skip, limit
