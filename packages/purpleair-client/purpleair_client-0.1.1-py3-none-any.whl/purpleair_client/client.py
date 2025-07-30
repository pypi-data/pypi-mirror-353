import requests
from .models import SensorData



class PurpleAirClient():

    BASE_URL = 'https://api.purpleair.com/v1'
    SENSOR_FIELDS = ["name","latitude","longitude", "pm2.5_alt", "pm2.5_alt_a", "pm2.5_alt_b", "pm2.5", "pm2.5_a", "pm2.5_b", "pm2.5_atm", "pm2.5_atm_a", "pm2.5_atm_b", "pm2.5_cf_1", "pm2.5_cf_1_a", "pm2.5_cf_1_b", "pm2.5_10minute"]
    HISTORY_FIELDS = ["pm2.5_alt_a", "pm2.5_alt_b", "pm2.5_atm_a", "pm2.5_atm_b", "pm2.5_cf_1_a", "pm2.5_cf_1_b"]
    


    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            'X-API-Key': self.api_key
        }
        self.last_request = None



    def get_sensor(self, sensor_id: int):
        """
        Fetch data from a single sensor

        Parameters:
            - sensor_id: sensor_index for the specific sensor
            - fields: list of fields to include in the response, defaults to fetch index, name, latitude, longitude and PM2.5 fields.

        Returns:
            - SensorData object with sensor information
        """
        
        url = f'{self.BASE_URL}/sensors/{sensor_id}'

        params = {}

       
        params['fields'] = ','.join(self.SENSOR_FIELDS)

        try:
            
            data = self.request_data(url, params)
            
            sensor = SensorData(
                index=data['sensor'].get('sensor_index'),
                name=data['sensor'].get('name'),
                lat=data['sensor'].get('latitude'),
                lon=data['sensor'].get('longitude'),
                pm2_5=data['sensor'].get('pm2.5'),
                pm2_5_a=data['sensor'].get('pm2.5_a'),
                pm2_5_b=data['sensor'].get('pm2.5_b'),
                pm2_5_alt=data['sensor'].get('pm2.5_alt'),
                pm2_5_alt_a=data['sensor'].get('pm2.5_alt_a'),
                pm2_5_alt_b=data['sensor'].get('pm2.5_alt_b'),
                pm2_5_atm=data['sensor'].get('pm2.5_atm'),
                pm2_5_atm_a=data['sensor'].get('pm2.5_atm_a'),
                pm2_5_atm_b=data['sensor'].get('pm2.5_atm_b'),
                pm2_5_cf_1=data['sensor'].get('pm2.5_cf_1'),
                pm2_5_cf_1_a=data['sensor'].get('pm2.5_cf_1_a'),
                pm2_5_cf_1_b=data['sensor'].get('pm2.5_cf_1_b'),
                pm2_5_10minute=data['sensor']['stats'].get('pm2.5_10minute')
                )
            
            sensor.aqiFromPM()
      
            return sensor

        except requests.RequestException as e:
            print(f"Request error: {e}")
            return

    def get_sensors(self, bound: dict):
        """
        Fetch data from sensors within a bounding box

        Parameters:
            - bound: Dictionary containing the northwest and southeast latitudes and longitudes that define the bounding box.
            Example:
                bound = {
                    "nwlat":float,
                    "nwlng":float,
                    "selat":float, 
                    "selng":float
                }
            - fields: list of fields to include in the response, defaults to fetch index, name, latitude, longitude and PM2.5 fields.
        Returns:
            - List of SensorData objects within the bounding box.
        """
        url = f'{self.BASE_URL}/sensors'

        params = {}

        sensorList = []

        params['nwlat'] = bound['nwlat']
        params['nwlng'] = bound['nwlng']
        params['selat'] = bound['selat']
        params['selng'] = bound['selng']

        if (self.last_request):
            params['modified_since'] = self.last_request

        params['fields'] = ','.join(self.SENSOR_FIELDS)

        
        try:
            data = self.request_data(url, params)

            if (data is None):
                return

            self.last_request = data['data_time_stamp']
            
            fields_list = data['fields']
            data_rows = data['data']

            field_idx = {field: i for i, field in enumerate(fields_list)}

            for row in data_rows:
        
                sensor = SensorData(
                    index=row[field_idx.get('sensor_index')],
                    name=row[field_idx.get('name')],
                    lat=row[field_idx.get('latitude')],
                    lon=row[field_idx.get('longitude')],
                    pm2_5=row[field_idx.get('pm2.5')],
                    pm2_5_a=row[field_idx.get('pm2.5_a')],
                    pm2_5_b=row[field_idx.get('pm2.5_b')],
                    pm2_5_alt=row[field_idx.get('pm2.5_alt')],
                    pm2_5_alt_a=row[field_idx.get('pm2.5_alt_a')],
                    pm2_5_alt_b=row[field_idx.get('pm2.5_alt_b')],
                    pm2_5_atm=row[field_idx.get('pm2.5_atm')],
                    pm2_5_atm_a=row[field_idx.get('pm2.5_atm_a')],
                    pm2_5_atm_b=row[field_idx.get('pm2.5_atm_b')],
                    pm2_5_cf_1=row[field_idx.get('pm2.5_cf_1')],
                    pm2_5_cf_1_a=row[field_idx.get('pm2.5_cf_1_a')],
                    pm2_5_cf_1_b=row[field_idx.get('pm2.5_cf_1_b')],
                    pm2_5_10minute=row[field_idx.get('pm2.5_10minute')]
                )

                sensor.aqiFromPM()
                sensorList.append(sensor)

            return sensorList
            
        except requests.RequestException as e:
            print(f"Request error: {e}")
            return
        

    def get_sensor_historic(self, sensor_id: int, start_timestamp: int, end_timestamp: int, average : int = 0):
        """
        Fetch historic data from a sensor using its index

        Parameters:
            - sensor_id: the sensor index
            - start_timestamp: The time stamp of the first required history entry in UNIX time stamp or ISO 8601 string
            - end_timestamp: The end time stamp of the history to return in UNIX time stamp or ISO 8601 string. (Not inclusive) 
            - fields: list of fields to include in the response, defaults to fetch index and PM2.5 fields.

        Returns:
            - List of SensorData objects contatinig the sensor's information.
        """
        url = f'{self.BASE_URL}/sensors/{sensor_id}/history'

        params = {}

        params['start_timestamp'] = start_timestamp
        params['end_timestamp'] = end_timestamp
        params['average'] = average

        params['fields'] = ','.join(self.HISTORY_FIELDS)
        
        try:
            data = self.request_data(url, params)

            if (data is None):
                return
            
            fields_list = data['fields']
            data_rows = data['data']

            sensorList = []

            field_idx = {field: i for i, field in enumerate(fields_list)}

            for row in data_rows:

                pm2_5_alt_a=row[field_idx.get('pm2.5_alt_a')]
                pm2_5_alt_b=row[field_idx.get('pm2.5_alt_b')]
                pm2_5_alt = self.get_average(pm2_5_alt_a, pm2_5_alt_b)

                pm2_5_atm_a = row[field_idx.get('pm2.5_atm_a')]
                pm2_5_atm_b = row[field_idx.get('pm2.5_atm_b')]
                pm2_5_atm = self.get_average(pm2_5_atm_a, pm2_5_atm_b)

                pm2_5_cf_1_a = row[field_idx.get('pm2.5_cf_1_a')]
                pm2_5_cf_1_b = row[field_idx.get('pm2.5_cf_1_b')]
                pm2_5_cf_1 = self.get_average(pm2_5_cf_1_a, pm2_5_cf_1_b)

                sensor = SensorData(
                    index=data['sensor_index'],
                    pm2_5_alt=pm2_5_alt,
                    pm2_5_alt_a=pm2_5_alt_a,
                    pm2_5_alt_b=pm2_5_alt_b,
                    pm2_5_atm=pm2_5_atm,
                    pm2_5_atm_a=pm2_5_atm_a,
                    pm2_5_atm_b=pm2_5_atm_b,
                    pm2_5_cf_1=pm2_5_cf_1,
                    pm2_5_cf_1_a=pm2_5_cf_1_a,
                    pm2_5_cf_1_b=pm2_5_cf_1_b,
                )

                sensor.aqiFromPM()
                sensorList.append(sensor)

            return sensorList
            
        except requests.RequestException as e:
            print(f"Request error: {e}")
            return


    def request_data(self, url: str, params: dict):
        response = requests.get(url, headers=self.headers, params=params)

        if not response.ok:
            print(f"API Error {response.status_code}: {response.json()['error']} - {response.json()['description']}")
            return
        
        return response.json()
    
    def get_average(self, *values):
        valid_values = [v for v in values if v is not None]
        if valid_values:
            return sum(valid_values) / len(valid_values)
        return None 
        