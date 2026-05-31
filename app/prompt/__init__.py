# prompt/__init__.py
# Public exports: router + service functions only.
# Do NOT import models, schemas, or internal modules here.

from app.prompt.router import router
from app.prompt.service import render_template, get_template

__all__ = [
    "router",
    "render_template",
    "get_template",
]
