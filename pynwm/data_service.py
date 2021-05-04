import json
import os

import numpy as np
import pandas as pd
import plotly.express as px
import requests

__all__ = ['ShortRange', 'MediumRange', 'LongRange']


class BaseClassNWM:
    station_id: int
    data: dict = {}
    urls: list = []
    df: pd.DataFrame = None
    range: str
    ensemble_options: list
    NWM_REST_BASE = 'https://nwmdata.nohrsc.noaa.gov/latest/forecasts'

    def __init__(self, station_id: int):
        self.station_id = station_id

    def __str__(self):
        return str(self.data)

    def _fetch_initial_data(self, mean: bool, ensembles: iter = '', use_examples: bool = False):
        if use_examples:
            with open(os.path.join(os.path.dirname(__file__), 'data', f'{self.range}.json')) as f:
                self.data = json.loads(f.read())
            return
        if self.range == 'short_range':
            self.urls = [f'{self.NWM_REST_BASE}/{self.range}/streamflow?station_id={self.station_id}', ]
            self.data = requests.get(self.urls[0]).json()
            return
        if mean:
            self.get_mean()
        if ensembles == 'all' or ensembles is True:
            ensembles = self.ensemble_options
        for ensemble in ensembles:
            self.get_ensemble(ensemble)

    def to_df(self):
        if self.df is not None:
            return self.df
        df = None
        for ensemble_number, nwm_json in self.data.items():
            csv_items = []
            for entry in nwm_json[0]['data']:
                csv_items.append([entry['forecast-time'], entry['value']])
            csv_items = np.array(csv_items)
            df_new = pd.DataFrame(csv_items[:, 1], index=csv_items[:, 0], columns=[nwm_json[0]['forecast-type']])
            df_new.index.name = 'datetime'
            df_new.index = pd.to_datetime(df_new.index)
            if df is None:
                df = df_new
            else:
                df = df.join(df_new)

        df = df.astype(float)
        self.df = df
        return self.df

    def to_csv(self):
        return self.to_df()

    def get_mean(self):
        if self.data.get('mean', None) is not None:
            return self.data['mean']
        url = f'{self.NWM_REST_BASE}/{self.range}_ensemble_mean/streamflow?station_id={self.station_id}'
        self.urls.append(url)
        self.data['mean'] = requests.get(url).json()
        return self.data['mean']

    def get_ensemble(self, number: int):
        if self.data.get(number, None) is not None:
            return self.data[number]
        url = f'{self.NWM_REST_BASE}/{self.range}_ensemble_member_{number}/streamflow?station_id={self.station_id}'
        self.urls.append(url)
        self.data[number] = requests.get(url).json()
        return self.data[number]

    def plot(self):
        if self.df is None:
            self.to_df()
        return px.line(self.df)


class ShortRange(BaseClassNWM):
    def __init__(self, station_id: int, use_examples: bool = False):
        super().__init__(station_id)
        self.range = 'short_range'
        self.ensemble_options = []
        self._fetch_initial_data(False, '', use_examples)

    def to_df(self):
        csv_items = []
        for entry in self.data[0]['data']:
            csv_items.append([entry['forecast-time'], entry['value']])
        csv_items = np.array(csv_items)
        df = pd.DataFrame(csv_items[:, 1], index=csv_items[:, 0], columns=[self.data[0]['forecast-type']])
        df.index.name = 'datetime'
        df.index = pd.to_datetime(df.index)

        df = df.astype(float)
        self.df = df
        return self.df


class MediumRange(BaseClassNWM):
    def __init__(self, station_id: int, mean: bool = True, ensembles: iter = '', use_examples: bool = False):
        super().__init__(station_id)
        self.range = 'medium_range'
        self.ensemble_options = [1, 2, 3, 4, 5, 6, 7]
        self._fetch_initial_data(mean, ensembles, use_examples)


class LongRange(BaseClassNWM):
    def __init__(self, station_id: int, mean: bool = True, ensembles: iter = '', use_examples: bool = False):
        super().__init__(station_id)
        self.range = 'long_range'
        self.ensemble_options = [1, 2, 3, 4]
        self._fetch_initial_data(mean, ensembles, use_examples)
