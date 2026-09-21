"""Runtime config + tunables. Secrets come from the environment (.env), never
from code."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

# --- Secrets (from .env) ---
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "market-gap-finder/0.1")

# --- Models (see cost control: capable by default, cost is your call) ---
# Sonnet 5 by default to keep runs at ~$1-3 (your call). Bump either to
# claude-opus-5 for richer player discovery / gap reasoning.
DISCOVERY_MODEL = os.getenv("DISCOVERY_MODEL", "claude-sonnet-5")
SYNTHESIS_MODEL = os.getenv("SYNTHESIS_MODEL", "claude-sonnet-5")

# --- Tunables ---
@dataclass(frozen=True)
class Settings:
    max_players: int = 8          # cap the competitive set (depth over breadth)
    reviews_per_source: int = 300  # pull cap per product per source
    primary_country: str = "gb"    # default storefront (Google Play, Trustpilot probe)
    apple_countries: tuple = ("gb", "us")  # Apple RSS is per-storefront; merges these
    # Worth-It Gate: skip a source for the whole run unless at least this many
    # products clear this many reviews on it.
    worth_it_min_reviews: int = 30
    worth_it_min_products: int = 2


settings = Settings()
