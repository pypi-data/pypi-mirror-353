from dataclasses import dataclass, field
from typing import Optional

@dataclass
class SensorData():
    index: int
    pm2_5_alt: Optional[float] = field(default=None)
    pm2_5_alt_a: Optional[float] = field(default=None)
    pm2_5_alt_b: Optional[float] = field(default=None)
    pm2_5_atm: Optional[float] = field(default=None)
    pm2_5_atm_a: Optional[float] = field(default=None)
    pm2_5_atm_b: Optional[float] = field(default=None)
    pm2_5_cf_1:Optional[float] = field(default=None)
    pm2_5_cf_1_a:Optional[float] = field(default=None)
    pm2_5_cf_1_b:Optional[float] = field(default=None)
    pm2_5_10minute: Optional[float] = field(default=None)
    aqi: Optional[float] = field(default=None)
    name : Optional[str]  = field(default=None)
    lat: Optional[float] = field(default=None)
    lon: Optional[float] = field(default=None)
    pm2_5: Optional[float] = field(default=None)
    pm2_5_a: Optional[float] = field(default=None)
    pm2_5_b: Optional[float] = field(default=None)

    def aqiFromPM(self):
        if (self.pm2_5_10minute is None):
            pm = self.pm2_5_atm
        else:
            pm = self.pm2_5_10minute
        if not float(pm):
            self.aqi = None
            return
        if pm == 'undefined'or pm < 0 or pm > 1000:
            self.aqi = None
            return
        
        """
                                            AQI   | RAW PM2.5    
        Good                               0 - 50 | 0.0 - 12.0    
        Moderate                         51 - 100 | 12.1 - 35.4
        Unhealthy for Sensitive Groups  101 - 150 | 35.5 - 55.4
        Unhealthy                       151 - 200 | 55.5 - 150.4
        Very Unhealthy                  201 - 300 | 150.5 - 250.4
        Hazardous                       301 - 400 | 250.5 - 350.4
        Hazardous                       401 - 500 | 350.5 - 500.4
        """

        if pm > 350.5:
            self.aqi = self.calcAQI(pm, 500, 401, 500.4, 350.5)  # Hazardous
        elif pm > 250.5:
            self.aqi = self.calcAQI(pm, 400, 301, 350.4, 250.5)  # Hazardous
        elif pm > 150.5:
            self.aqi = self.calcAQI(pm, 300, 201, 250.4, 150.5)  # Very Unhealthy
        elif pm > 55.5:
            self.aqi = self.calcAQI(pm, 200, 151, 150.4, 55.5)  # Unhealthy
        elif pm > 35.5:
            self.aqi = self.calcAQI(pm, 150, 101, 55.4, 35.5)  # Unhealthy for Sensitive Groups
        elif pm > 12.1:
            self.aqi =  self.calcAQI(pm, 100, 51, 35.4, 12.1)  # Moderate
        elif pm >= 0:
            self.aqi =  self.calcAQI(pm, 50, 0, 12, 0)  # Good
        else:
            self.aqi = None

    def calcAQI(self, Cp: float, Ih: int, Il: int, BPh: float, BPl: float):
        a = (Ih - Il)
        b = (BPh - BPl)
        c = (Cp - BPl)
        return round((a / b) * c + Il)