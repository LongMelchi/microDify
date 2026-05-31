"""Common API router — placeholder, no endpoints defined yet.

Storage, queue administration, and rate-limit introspection endpoints
can be added here when needed.
"""

from fastapi import APIRouter

router = APIRouter(
    prefix="/common",
    tags=["common"],
)
