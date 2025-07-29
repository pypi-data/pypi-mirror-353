"""
USMS constants.

This module defines the constants for this USMS package.
"""

from datetime import timedelta
from zoneinfo import ZoneInfo

from usms.models.tariff import USMSTariff, USMSTariffTier

BRUNEI_TZ = ZoneInfo("Asia/Brunei")

ELECTRIC_UNIT = "kWh"
WATER_UNIT = "m³"

ELECTRIC_TARIFF = USMSTariff(
    [
        USMSTariffTier(1, 600, 0.01),
        USMSTariffTier(601, 2000, 0.08),
        USMSTariffTier(2001, 4000, 0.10),
        USMSTariffTier(4001, float("inf"), 0.12),
    ]
)
WATER_TARIFF = USMSTariff(
    [
        USMSTariffTier(1, 54.54, 0.11),
        USMSTariffTier(54.54, float("inf"), 0.44),
    ]
)

UNITS = {
    "ELECTRIC": ELECTRIC_UNIT,
    "WATER": WATER_UNIT,
}
TARIFFS = {
    "ELECTRIC": ELECTRIC_TARIFF,
    "WATER": WATER_TARIFF,
}

UPDATE_INTERVAL = timedelta(seconds=60 * 60)
REFRESH_INTERVAL = timedelta(seconds=60 * 15)
