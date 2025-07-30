import sys
if "pytest" in sys.modules:
    from wu_api.WeatherUndergroundAPI import WeatherUndergroundAPI
else:
    from bgp_data_interface.wu_api.WeatherUndergroundApi import WeatherUndergroundAPI

import pandas as pd
from typing import Dict, Any

class WeatherUnderground:

    _wu: WeatherUndergroundAPI

    def __init__(self) -> None:
        self._wu = WeatherUndergroundAPI()

    # def forecast(self, params: Dict[str, Any]) -> pd.DataFrame:
    #     return self._wu.forecast(params)

    def historical(self, params: Dict[str, Any]) -> pd.DataFrame:
        return self._wu.historical(params)
