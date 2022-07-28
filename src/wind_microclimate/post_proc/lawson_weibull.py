import math
import pandas as pd
import numpy as np

from post_proc.lawson import LawsonLDDC


class LawsonEpw(LawsonLDDC):

    def __init__(self, case, angles, weather, csv_vr, csv_lawson, receptors):
        super().__init__(case, angles, weather, csv_vr, csv_lawson, receptors)

    def wind_microclimate(self, safety=True):
        """ Read VR results and weather data, then run wind comfort calculation. """
        csv_input = self.weather.find_weibull()
        self.dfs_weibull = [pd.read_csv(csv, header=0) for csv in csv_input]
        if safety:
            df_saf = [df for df in self.dfs_weibull if 'annual' in df.name][0]
            self.dfs_weibull.remove(df_saf)
        for df_weibull, csv_in in zip(self.dfs_weibull, csv_input):
            csv_lawson_season = f'{self.csv_lawson.rstrip(".csv")}_{csv_in}'
            self.p_exceed = np.zeros((len(self.dfs_vr[0]), 
                len(self.thresh_ws['Comfort'])), dtype=float)
            dfs = {'Comfort': df_weibull}
            if df_saf is not None:
                dfs['Safety'] = df_saf
            for idx, vrs in enumerate(zip(*self.vr_gens)):
                self.p_exceed[idx] += self.exceedance_weibull(vrs, dfs)
            self.calculate_classes(csv_lawson_season)

    def exceedance_weibull(self, vrs, dfs_weibull):
        """ Calculate exceedance of given wind speed thresholds using Weibull 
            distribution parameters """
        weibull_f = lambda x, p, v, k: p * math.exp(-pow(x/v, k))
        thresh_exceed = {'Comfort': [], 'Safety': []}
        for key, df in dfs_weibull:
            df['v'] = df['c'] * vrs
            for threshold in sorted(self.thresh_ws[key]):
                df['weibull'] = df.apply(lambda row: weibull_f(threshold, row['p'], 
                    row['v'], row['k']), axis=1)
                thresh_exceed[key].append(df['weibull'].sum())
        return sum(thresh_exceed.values(), [])