# old minimal test, without HA
from uuid import uuid4
import asyncio
from const import CONF_EMAIL, CONF_PASSWORD
import light_scheduler
import light_config
from light_config import ConfigEntry
from custom_components.daikin_residential_altherma import init_tokenset, async_setup_entry  # , async_setup
from custom_components.daikin_residential_altherma.const import DOMAIN, CONF_TOKENSET



async def main_task():
    hass = light_scheduler.HomeScheduler()
    success, data = await init_tokenset(hass, "turvas@gmail.com",  "tulin2Dai")
    if not success:
        print(f"ERROR: {data}")
        return 1
    entry = ConfigEntry(
        2,
        DOMAIN,
        "Test",
        {"installed_app_id": str(uuid4()),
         CONF_EMAIL: "turvas@gmail.com",
         CONF_PASSWORD: "tulin2Dai",
         CONF_TOKENSET: data,
         },
        "user",
    )
    hass.config_entries = light_config.ConfigEntries(hass, None)
    await hass.config_entries.async_add(entry)
    await async_setup_entry(hass, entry)
    return 0


async def main():
    return await asyncio.gather(main_task())


if __name__ == "__main__":
    asyncio.run(main())

