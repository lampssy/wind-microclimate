import numpy as np

from wind_microclimate.post_proc.lawson import LawsonLDDC


class LawsonEpw(LawsonLDDC):

    def __init__(self, case_dir, case, angles, weather, csv_vr, csv_lawson, receptors):
        super().__init__(case_dir, case, angles, csv_vr, csv_lawson, receptors)
        self.weather = weather

    def wind_microclimate(self, safety=True, receptors=False):
        """ Read VR results and weather data, then run wind comfort calculation. """
        self.weather.epw_to_df()
        dfs_ws = [self.weather.group_wind_data(df, self.angles, self.weather.wd_col)
                  for df in self.weather.wind_data]
        if safety:
            # to be modified if seasonal epw dataframes introduced
            df_saf = dfs_ws[0]
        for df_ws in dfs_ws:
            # split epw weather dataframe into particular wind directions
            grouped_df = [df_ws[df_ws['Direction'] == angle] for angle in self.angles]
            self.p_exceed = self.exceedance_epw(grouped_df)
            self.calculate_classes(self.csv_lawson, receptors=receptors)

    def exceedance_epw(self, dfs_epw):
        """ Calculate exceedance of given wind speed thresholds using typical 
            meteorological year weather data from epw file """
        vr_gens = [(vr for vr in df_vr['VR'].tolist()) for df_vr in self.dfs_vr]
        multiplied = [[vr * df_epw[self.weather.ws_col] for vr in vr_point] 
            for vr_point, df_epw in zip(vr_gens, dfs_epw)]
        exceedance = np.zeros((len(self.dfs_vr[0]), len(self.thresh_ws_values)))
        for l in multiplied:
            for idx, s in enumerate(l):
                for n, threshold in enumerate(self.thresh_ws_values):
                    exceedance[idx][len(self.thresh_ws_values) - n - 1] += \
                        s[s > threshold].count()
        return exceedance / 8760
        # sprawdzic czy potrzebne rozdzielenie na comfort i safety