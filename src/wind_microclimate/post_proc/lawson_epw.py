import time
import numpy as np

from post_proc.lawson import LawsonLDDC


class LawsonEpw(LawsonLDDC):

    def __init__(self, case, angles, weather, csv_vr, csv_lawson, receptors):
        super().__init__(case, angles, weather, csv_vr, csv_lawson, receptors)

    def wind_microclimate(self, safety=True):
        """ Read VR results and weather data, then run wind comfort calculation. """
        wind_data = self.weather.epw_to_df(self.weather.data_file)
        dfs_ws = [self.weather.group_wind_data(df, self.angles, 'winddir') for df in wind_data]
        if safety:
            # to be modified if seasonal epw dataframes introduced
            df_saf = dfs_ws[0]
        for df_ws in dfs_ws:
            # split epw weather dataframe into particular wind directions
            grouped_df = [df_ws[df_ws['Direction'] == angle] for angle in self.angles]
            start = time.time()
            self.p_exceed = self.exceedance_epw(grouped_df)
            end = time.time()
            print(end-start)
            self.calculate_classes(self.csv_lawson)

    def exceedance_epw(self, dfs_epw):
        """ Calculate exceedance of given wind speed thresholds using typical 
            meteorological year weather data from epw file """
        multiplied = [[vr * df_epw['wind speed'] for vr in vr_point] 
            for vr_point, df_epw in zip(self.vr_gens, dfs_epw)]
        exceedance = np.zeros((len(self.dfs_vr[0]), len(self.thresh_ws_values)))
        for l in multiplied:
            for idx, s in enumerate(l):
                for n, threshold in enumerate(self.thresh_ws_values):
                    exceedance[idx][len(self.thresh_ws_values) - n - 1] += \
                        s[s > threshold].count()
        return exceedance / 8760
        # sprawdzic czy potrzebne rozdzielenie na comfort i safety