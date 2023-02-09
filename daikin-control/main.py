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
from custom_components.daikin_residential_altherma import async_setup_entry, DaikinApi  # , async_setup
from custom_components.daikin_residential_altherma.const import DOMAIN, CONF_TOKENSET

_LOGGER = logging.getLogger(__name__)
username = "turvas@gmail.com"
password = "tulin2Dai"

tokenfile = "tokens.json"

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
            print(f"{dev.desc['timestamp']}: leaving water: {dev.leaving_water_temperature}C, tank temp: {dev.tank_temperature}C, tank heating: {dev.tank_is_in_warning_state}")


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
    print_status(daikin_data)
    return 0


async def main():
    return await asyncio.gather(main_task())


if __name__ == "__main__":
    asyncio.run(main())
