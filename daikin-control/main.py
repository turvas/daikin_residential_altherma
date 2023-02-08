# old minimal test, without HA
from uuid import uuid4
import asyncio
from const import CONF_EMAIL, CONF_PASSWORD
import light_scheduler
import light_config
from light_config import ConfigEntry
from custom_components.daikin_residential_altherma import async_setup_entry, DaikinApi  # , async_setup
from custom_components.daikin_residential_altherma.const import DOMAIN, CONF_TOKENSET

username = "turvas@gmail.com"
password = "tulin2Dai"


async def init_tokenset(hass, email, password):
    """:returns tuple of (success: bool, errortext: str | tokenset: Dict) """
    try:
        daikin_api = DaikinApi(hass, None)
    except Exception as e:
        _LOGGER.error("Failed to initialize DaikinApi: %s", e)
        return False, "init_failed"
    try:
        await daikin_api.retrieveAccessToken(email, password)
    except Exception as e:
        _LOGGER.error("Failed to retrieve Access Token: %s", e)
        return False, "token_retrieval_failed"
    try:
        await daikin_api.getApiInfo()
    except Exception as e:
        _LOGGER.error("Failed to connect to DaikinApi: %s", e)
        return False, "cannot_connect"

    return True, daikin_api.tokenSet


async def main_task():
    """ main async entrypoint """
    hass = light_scheduler.HomeScheduler()
    hass.config_entries = light_config.ConfigEntries(hass, None)
    success, data = await init_tokenset(hass, username, password)
    if not success:
        print(f"ERROR: {data}")
        return 1
    entry = ConfigEntry(2, DOMAIN, "Test",
        {"installed_app_id": str(uuid4()), CONF_EMAIL: username, CONF_PASSWORD: password, CONF_TOKENSET: data},
        "user")
    await hass.config_entries.async_add(entry)
    await async_setup_entry(hass, entry)
    return 0


async def main():
    return await asyncio.gather(main_task())


if __name__ == "__main__":
    asyncio.run(main())

