# PurpleAirClient

## Getting started

Import the PurpleAirClient class:

```python
from purpleair_client import PurpleAirClient
```
Create your client with your PurpleAir API Key
```python
purpleAir = PurpleAirClient(API-KEY)
```

## Methods


#### 1. ```get_sensor(sensor_ID)```

Fetch data from a single sensor using the sensor index, fetches sensor index, name, latitude, longitude PM2.5 realtime fields and PM2.5_10 minute average field.


__Parameters:__
- ```sensor_id```: sensor_index for the specific sensor

__Returns:__
- SensorData object with sensor information

#### 2. ```get_sensors(bound)```


Fetch data from sensors within a bounding box. For each seansor fetches sensor index, fetches sensor index, name, latitude, longitude PM2.5 realtime fields and PM2.5_10 minute average field.


__Parameters:__

- ```bound```: Dictionary containing the northwest and southeast latitudes and longitudes that define the bounding box.

Example: 
```
bound = {
    "nwlat":float,
    "nwlng":float,
    "selat":float, 
    "selng":float
}
```


__Returns:__
- List of SensorData objects within the bounding box.

#### 3. ```get_sensor_historic(sensor_id, start_timestamp, end_timestamp, average)```


Fetch historic data from a sensor using its index. 

Parameters:
- ```sensor_id```: the sensor index
- ```start_timestamp```: The time stamp of the first required history entry in UNIX time stamp or ISO 8601 string
- ```end_timestamp```: The end time stamp of the history to return in UNIX time stamp or ISO 8601 string. (Not inclusive) 
- ```average```: 	The desired average in minutes. The amount of data that can be returned in a single response depends on the average used in the request. [See API documentation here](https://api.purpleair.com/#api-sensors-get-sensor-history)

Returns:
- List of SensorData objects contatinig the sensor's information. Fetches PM2.5 values.


## Example:

```
from purpleair_client import PurpleAirClient

purpleAir = PurpleAirClient(API-KEY)

bounding_box = {
    "nwlat":4.674529,
    "nwlng":-74.104295,
    "selat":4.614464, 
    "selng":-74.064736
}

start_time = "1717650000"
end_time = "1717657200"

sensor_data = purpleAir.get_sensor_historic("143910", start_time, end_time, 10)
sensors_data = purpleAir.get_sensor("143910")
sensor_historic_data = purpleAir.get_sensors(bounding_box)

print(sensor_data)
print(sensors_data)
print(sensor_historic_data)

```