import pandas as pd


class WeatherData:

    def __init__(self, data_file):
        self.data_file = data_file
        self.ws_col = 'windspeed'
        self.wd_col = 'winddir'
    
    def group_wind_data(self, df_wind, angles, wd_col):
        """ Assign wind angle group to each record in weather data """
        interval = angles[1] - angles[0]
        df_wind['Direction'] = 0
        for angle in angles:
            mask_angle = (df_wind[wd_col].between(angle - interval/2, 
                angle + interval/2, inclusive='right'))
            df_wind.loc[mask_angle, 'Direction'] = angle
        return df_wind

    def group_seasons(self, df_wind, date_col):
        """ Assign season to each record in weather data """
        df_wind[date_col] = pd.to_datetime(df_wind[date_col])
        df_wind[date_col] = df_wind[date_col].apply(lambda x: x.timetuple().tm_yday)
        # days of year
        mask_spring = (df_wind[date_col].between(80, 172, inclusive='left'))
        mask_summer = (df_wind[date_col].between(172, 264, inclusive='left'))
        mask_fall = (df_wind[date_col].between(264, 355, inclusive='left'))
        df_wind['Season'] = 'winter'
        df_wind.loc[mask_spring, 'Season'] = 'spring'
        df_wind.loc[mask_summer, 'Season'] = 'summer'
        df_wind.loc[mask_fall, 'Season'] = 'autumn'
        return df_wind
