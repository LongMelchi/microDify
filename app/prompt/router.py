# prompt/router.py
# Route declarations only — inject Depends, call service, return result.
# No DB queries, no ORM, no business logic, no external API calls.
# Max 150 lines; split into sub-routers when exceeded.

from fastapi import APIRouter

router = APIRouter(prefix="/prompt", tags=["prompt"])

# Endpoints will be added here as the module is built out.
