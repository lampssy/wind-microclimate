from pyepw.epw import EPW
import sys, glob
import pandas as pd
from logging import info, warning, error, exception

from weather.weather import WeatherData


class EpwWeatherData(WeatherData):

    def __init__(self):
        data_file = self.find_epw()
        self.v_ref = self.mean_ws_epw()
        super().__init__(data_file)
    

    def find_epw(self):
        """ Return name of the epw file in the current directory """

        epw_files = glob.glob('*.epw')
        if len(epw_files) == 0:
            sys.exit(error('\nThere is no EPW file in this directory\n'))
        elif len(epw_files) > 1:
            sys.exit(error('\nThere is more than one EPW file in this directory,',
                'please remove unnecessary files\n'))
        else:
            self.data_file = epw_files[0]


    def epw_to_df(self):
        """ Return dataframe with wind speeds and directions from the epw file """

        epw = EPW()
        df_list = []
        try:
            epw.read(self.data_file)
            wind_dat = []
            for w in epw.weatherdata:
                wind_dat.append([w.wind_direction, w.wind_speed])
            # separate dataframes for seasons planned as a future development
            df_list.append(pd.DataFrame(wind_dat, columns=[self.wd_col, self.ws_col]))
            self.wind_data = df_list
        except FileNotFoundError:
            exception(f'\n{self.data_file} file not found\n')
            sys.exit()


    def mean_ws_epw(self):
        epw = EPW()
        epw.read(self.data_file)
        sum = 0
        for w in epw.weatherdata:
            sum += w.wind_speed
        self.mean_ws = sum / 8760