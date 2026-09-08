"""Test fixtures for the Kermi x-center integration.

``pytest-homeassistant-custom-component`` registers itself through an entry
point, so it needs no ``pytest_plugins`` declaration here.
"""

import pytest


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Load the integration from custom_components in every test."""
    return
