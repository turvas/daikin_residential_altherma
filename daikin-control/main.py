# old minimal test, without HA
import datetime
from uuid import uuid4
import asyncio
import json
import logging
from const import CONF_EMAIL, CONF_PASSWORD
import light_scheduler
import light_config
from light_config import ConfigEntry
from custom_components.daikin_residential_altherma import async_setup_entry, DaikinApi
from custom_components.daikin_residential_altherma.switch import DaikinSwitch
from custom_components.daikin_residential_altherma.climate import DaikinClimate
from custom_components.daikin_residential_altherma.const import DOMAIN, DAIKIN_DEVICES, CONF_TOKENSET, DAIKIN_SWITCHES

_LOGGER = logging.getLogger(__name__)
username = "turvas@gmail.com"
password = "tulin2Dai"

tokenfile = "tokens.json"
gl_switches = {}

async def init_tokenset(hass, email, _password):
    """:returns tuple of (success: bool, errortext: str | tokenset: Dict) """
    try:
        daikin_api = DaikinApi(hass, None)
    except Exception as e:
        _LOGGER.error("Failed to initialize DaikinApi: %s", e)
        return False, "init_failed"
    try:
        await daikin_api.retrieveAccessToken(email, _password)
    except Exception as e:
        _LOGGER.error("Failed to retrieve Access Token: %s", e)
        return False, "token_retrieval_failed"
    try:
        await daikin_api.getApiInfo()
    except Exception as e:
        _LOGGER.error("Failed to connect to DaikinApi: %s", e)
        return False, "cannot_connect"

    return True, daikin_api.tokenSet


def read_token_file():
    try:
        with open(tokenfile) as f:
            data = json.load(f)
        gen_txt = data.get('generated')
        expires = data.get('expires_in')
        if gen_txt and expires:
            now = datetime.datetime.now()
            generated = datetime.datetime.fromisoformat(gen_txt)
            if generated.timestamp() + expires < now.timestamp():  # too old
                return None
        return data
    except FileNotFoundError:
        return None

def save_token_file(data):

    now = datetime.datetime.now()
    data['generated'] = now.isoformat()
    with open(tokenfile, 'w') as f:
        json.dump(data, f)  # data is dict


def print_status(daikin_data: dict):
    if daikin_data:
        devices = daikin_data.get('daikin_devices')
        for _, dev in devices.items():     # iterate Appliances
            print(f"{dev.desc['timestamp']}: leaving water: {dev.leaving_water_temperature}C, "
                  f"tank temp: {dev.tank_temperature}C")

async def setup_climate(hass):
    """Set up Daikin climate based on config_entry."""
    for dev_id, device in hass.data[DOMAIN][DAIKIN_DEVICES].items():
        climate = DaikinClimate(device)
    return climate


async def set_heating_temp_shift(climate: DaikinClimate, temp: float):
    """:param temp - shift from normal"""
    args = {'temperature': temp}
    return await climate.async_set_temperature(**args)


async def setup_switches(hass):
    """Set up Daikin tank based on config_entry."""
    global gl_switches
    for dev_id, device in hass.data[DOMAIN][DAIKIN_DEVICES].items():
        switches = DAIKIN_SWITCHES

        for switch in switches:
            if device.support_preset_mode(switch):
                _LOGGER.info("DAMIANO Adding Switch {}".format(switch))
                gl_switches[switch] = DaikinSwitch(device, switch)


async def set_tank_state(on=True):
    """Hot water tank power control"""
    sw = gl_switches.get('Tank')
    if sw:  # DaikinSwitch
        if on:
            await sw.async_turn_on()
        else:
            await sw.async_turn_off()


async def main_task():
    """ main async entrypoint """
    hass = light_scheduler.HomeScheduler()
    hass.config_entries = light_config.ConfigEntries(hass, None)
    data = read_token_file()
    if not data:
        success, data = await init_tokenset(hass, username, password)   # ask new tokens
        if not success:
            print(f"ERROR: {data}")
            return 1
        save_token_file(data)
    entry = ConfigEntry(2, DOMAIN, "Test",
        {"installed_app_id": str(uuid4()), CONF_EMAIL: username, CONF_PASSWORD: password, CONF_TOKENSET: data},
        "user")
    await hass.config_entries.async_add(entry)
    await async_setup_entry(hass, entry)
    daikin_data = hass.data[DOMAIN]
    await setup_switches(hass)
    climate = await setup_climate(hass)
    await set_tank_state(True)
    await set_heating_temp_shift(climate, 5.0)
    print_status(daikin_data)
    return 0


async def main():
    return await asyncio.gather(main_task())


if __name__ == "__main__":
    asyncio.run(main())
