import os, sys, glob
import pandas as pd
from logging import error
from reliability.Fitters import Fit_Weibull_2P
from reliability.Other_functions import histogram
import matplotlib.pyplot as plt
from pathlib import Path

from weather.weather import WeatherData


class WeibullWeatherData(WeatherData):

    def __init__(self, data_file, weibull_vref, angles, output_dir, plot=False,
                 plot_dir='weibull_fit'):
        super().__init__(data_file)
        self.v_ref = weibull_vref
        self.angles = angles
        self.output_dir = Path(output_dir)
        self.plot = plot
        self.plot_dir = plot_dir
        self.date_col = 'datetime'

    def prepare_weibull(self):
        """ Read csv file with weather data to dataframe, convert mph to m/s, 
            group by seasons and apply write_weibull per each group """
        data = pd.read_csv(self.data_file, usecols=[self.date_col, self.ws_col, 
            self.wd_col])
        # fill NaNs with values from previous/next rows
        data.fillna(method='bfill', inplace=True)
        data.fillna(method='ffill', inplace=True)
        # convert mph to m/s
        data[self.ws_col] = data[self.ws_col] * 0.44704
        # replace 0 m/s wind speed with 0.1 m/s - 0 not possible in Weibull
        data[self.ws_col] = data[self.ws_col].mask(data[self.ws_col]==0).fillna(0.1)
        # assign seasons to weather data
        df_seasons = self.group_seasons(data, self.date_col)
        # assign wind angle groups to wind directions in weather data
        df_angles = self.group_wind_data(df_seasons, self.angles, self.wd_col)
        gb_season = df_angles.groupby('Season')
        # seasonal Weibull parameters
        gb_season.apply(lambda x: self.write_weibull(x, x.name))
        # annual Weibull parameters
        self.write_weibull(df_angles, 'annual')

    def write_weibull(self, gb, season):
        """ Group the dataframe by wind angle, apply weibull_params per each 
            group and write parameters to csv file """
        # n of weather data records per season
        n_records = gb['Direction'].count()
        gb_angle = gb.groupby('Direction')
        params = []
        # calculate Weibull parameters for each angle group
        gb_angle.apply(lambda x: params.append(self.weibull_params(
            x['windspeed'].values.tolist(), n_records, x.name, season)))
        self.df_weibull = pd.DataFrame(params, columns=['Direction', 'p', 'c', 'k'])
        self.df_weibull.to_csv(self.output_dir / 'weibull_{0}.csv'.format(season),
                               index=False)

    def weibull_params(self, wind_speeds, n_records, group, season):
        """ Fit Weibull distribution to given wind speed data and save the PDF 
            fnction to a file (plot=True); return wind angle, wind angle 
            probability and Weibull shape and scale parameters """
        # probability of wind direction
        wind_p = len(wind_speeds)/n_records
        # fit Weibull dist to wind speed data
        self.wb = Fit_Weibull_2P(failures=wind_speeds, show_probability_plot=False,
            print_results=False)
        if self.plot:
            self.plot_weibull(wind_speeds, season, group)
        return [group, wind_p, self.wb.alpha, self.wb.beta]

    def find_weibull(self, weibull_dir='.'):
        """ Return names of the csv files with Weibull parameters in the given 
            directory (current directory as a default). """
        weibull_csv = glob.glob('weibull*.csv')
        if len(weibull_csv) == 0:
            sys.exit(error('CSV files with Weibull factors not found'))
        else:
            return weibull_csv

    def plot_weibull(self, wind_speeds, season, group):
        Path(self.plot_dir).mkdir(parents=True, exist_ok=True)
        histogram(wind_speeds)
        self.wb.distribution.PDF(label='Fit_Weibull_2P')
        plt.title(f'Fitting Weibull distribution for {season}, {group} deg')
        plt.xlabel('wind speed')
        plt.legend()
        plt.savefig(os.path.join(self.plot_dir, f'{season}-{group}-deg.png'))
        plt.close()
