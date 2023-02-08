* * * * * * INSERTING A NEW SENSOR * * * * * *


1) const.py: Add a constant ATTR by naming it the
new name, eg:

        ATTR_TANK_TEMPERATURE = "tankTemperature"


2) const.py: Add the CMD_SET with the path MP,DP e
Value:

       DAIKIN_CMD_SETS = {
         ATTR_TANK_TEMPERATURE: [MP_DOMESTIC_HWT, DP_SENSORS, "/tankTemperature"],
         ...
       }

where "/tankTemperature" must match the JSON:

                 "sensoryData": {
                     "ref": "#sensoryData",
                     "settable": false,
                     "value": {
                         "tankTemperature": {
                             "maxValue": 127,
                             "minValue": -127,
                             "requiresReboot": false,
                             "settable": false,
                             "stepValue": 1,
                             "value": 38


3) const.py: in the SENSOR_TYPES add the definition of the new sensor:


    SENSOR_TYPES = {
      ...
      ATTR_TANK_TEMPERATURE: {
      CONF_NAME: "Tank Temperature",
      CONF_TYPE: SENSOR_TYPE_TEMPERATURE,
      CONF_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE,
      CONF_UNIT_OF_MEASUREMENT: TEMP_CELSIUS,
    },


4) daikin_base.py: add the attribute to the import:


    from .const import(
      ...,
      ATTR_TANK_TEMPERATURE,


5) daikin_base.py: define the new properties "support_xxx" and "xxx":


     @property
     def support_tank_temperature(self):
         """Return True if the device supports tank temperature measurement."""
         return self.getData(ATTR_TANK_TEMPERATURE) is not None

     @property
     def tank_temperature(self):
         """Return current tank temperature."""
         return float(self.getValue(ATTR_TANK_TEMPERATURE))


6) sensor.py: add the attribute to the import:


    from .const import (
      ...,
      ATTR_TANK_TEMPERATURE,


7) sensor.py: Append If the sensor is supported


         if device.support_tank_temperature:
             sensor = DaikinSensor.factory(device, ATTR_TANK_TEMPERATURE)
             _LOGGER.debug("DAMIANO append sensor = %s", sensor)
             sensors.append(sensor)


8) sensor.py: Add the state property


    @property
    def state(self):
    """Return the internal state of the sensor."""
      ...
      if self._device_attribute == ATTR_TANK_TEMPERATURE:
        return self._device.tank_temperature
      return None


9) in case of new sensor types (see example for "SENSOR_TYPE_INFO: DaikinInfoSensor"):

9A) Add new "SENSOR_TYPE" in const.py.

    SENSOR_TYPE_INFO = None

9B) Add the new SENSOR_TYPE among the SENSOR_TYPES in const.py.
  The unit of measurement must still be filled in...

    ATTR_CONTROL_MODE: {
         CONF_NAME: "Info Control Mode",
         CONF_TYPE: None,
         CONF_ICON: "mdi:information-outline",
         CONF_UNIT_OF_MEASUREMENT: " ",
     },

9C) Import the new attribute into sensor.py

    from .const import (
        DOMAIN as DAIKIN_DOMAIN,
        DAIKIN_DEVICES,
        ATTR_COOL_ENERGY,
        ...,
        ATTR_CONTROL_MODE,


9E) Add the new SENSOR_TYPE to the factory def in sensor.py

             cls = {
                 SENSOR_TYPE_TEMPERATURE: DaikinClimateSensor,
                 SENSOR_TYPE_POWER: DaikinEnergySensor,
                 SENSOR_TYPE_ENERGY: DaikinEnergySensor,
                 SENSOR_TYPE_INFO: DaikinInfoSensor,
             }[SENSOR_TYPES[monitored_state][CONF_TYPE]]
             return cls(device, monitored_state, period)

9E) Add the class for the new SENSOR_TYPE in sensor.py
with the two @properties as in the example.

    class DaikinInfoSensor(DaikinSensor):
    """Representation of a Climate Sensor."""
    
    @property
    def state(self):
        """Return the internal state of the sensor."""
        if self._device_attribute == ATTR_CONTROL_MODE:
            return self._device.control_mode
    
    @property
    def state_class(self):
        return STATE_CLASS_MEASUREMENT