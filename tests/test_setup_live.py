"""Set the integration up against a real x-center and list what it produced.

Skipped unless KERMI_HOST is set, so it never runs in CI. It exists to check
the whole path — config entry, shared modbus connection, coordinator, every
platform — against hardware rather than a mock.

    KERMI_HOST=10.0.1.21 pytest tests/test_setup_live.py -s
"""

import os

import pytest
import pytest_socket
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.kermi_xcenter.const import DEFAULT_UNIT_IDS, DOMAIN

HOST = os.environ.get("KERMI_HOST")

pytestmark = pytest.mark.skipif(not HOST, reason="KERMI_HOST is not set")


@pytest.fixture
def allow_controller(socket_enabled: None):
    """Let this one test reach the controller.

    The Home Assistant test harness blocks outbound sockets and pins the
    allow-list to localhost at session start, so widening it has to happen per
    test rather than through the --allow-hosts option.
    """
    pytest_socket.socket_allow_hosts([HOST, "127.0.0.1"], allow_unix_socket=True)
    yield
    pytest_socket.socket_allow_hosts(["127.0.0.1"], allow_unix_socket=True)


async def test_sets_up_against_real_hardware(
    hass: HomeAssistant, allow_controller: None
) -> None:
    """Configure the integration and report the devices and entities created."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOST: HOST, CONF_PORT: 502, **DEFAULT_UNIT_IDS},
        unique_id=f"{HOST}_502",
    )
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entities = er.async_get(hass)
    devices = dr.async_get(hass)
    registered = er.async_entries_for_config_entry(entities, entry.entry_id)
    device_entries = dr.async_entries_for_config_entry(devices, entry.entry_id)

    print(f"\n{len(device_entries)} devices, {len(registered)} entities\n")
    for device in device_entries:
        print(f"  device: {device.name}")
        for item in registered:
            if item.device_id != device.id:
                continue
            state = hass.states.get(item.entity_id)
            print(f"    {item.entity_id:<66} {state.state if state else '(disabled)'}")

    assert device_entries, "no devices were created"
    assert registered, "no entities were created"

    # The heat pump must have produced a real outdoor temperature.
    outdoor = next(
        (
            hass.states.get(item.entity_id)
            for item in registered
            if item.entity_id.endswith("outdoor_temperature")
        ),
        None,
    )
    assert outdoor is not None, "no outdoor temperature entity"
    assert outdoor.state not in ("unknown", "unavailable"), outdoor.state
    print(f"\n  outdoor temperature reads {outdoor.state} °C")

    assert await hass.config_entries.async_unload(entry.entry_id)
