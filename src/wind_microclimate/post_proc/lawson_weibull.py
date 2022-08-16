import math, os
import pandas as pd
import numpy as np

from post_proc.lawson import LawsonLDDC


class LawsonWeibull(LawsonLDDC):

    def __init__(self, case_dir, case, angles, weather, csv_vr, csv_lawson, receptors):
        super().__init__(case_dir, case, angles, csv_vr, csv_lawson, receptors)
        self.weather = weather

    def wind_microclimate(self, safety=True):
        """ Read VR results and weather data, then run wind comfort calculation. """
        self.weather.prepare_weibull()
        csv_input = self.weather.find_weibull(weibull_dir=self.weather.output_dir)
        self.dfs_weibull = [pd.read_csv(csv, header=0) for csv in csv_input]
        if safety:
            df_saf = [df for idx, df in enumerate(self.dfs_weibull) 
                      if 'annual' in csv_input[idx]][0]
        for df_weibull, csv_in in zip(self.dfs_weibull, csv_input):
            # TO DO: check if this is efficient
            vr_gens = [(vr for vr in df_vr['VR'].tolist()) for df_vr in self.dfs_vr]
            csv_lawson_season = f'{self.csv_lawson.rstrip(".csv")}_{os.path.split(csv_in)[1]}'
            self.p_exceed = np.zeros((len(self.dfs_vr[0]),
                len(sum(self.thresh_ws.values(), []))), dtype=float)
            dfs = {'Comfort': df_weibull}
            if df_saf is not None:
                dfs['Safety'] = df_saf
            for idx, vrs in enumerate(zip(*vr_gens)):
                self.p_exceed[idx] += self.exceedance_weibull(vrs, dfs)
            self.calculate_classes(csv_lawson_season)

    def exceedance_weibull(self, vrs, dfs_weibull):
        """ Calculate exceedance of given wind speed thresholds using Weibull 
            distribution parameters """
        weibull_f = lambda x, p, v, k: p * math.exp(-pow(x/v, k))
        thresh_exceed = {'Comfort': [], 'Safety': []}
        for key, df in dfs_weibull.items():
            df['v'] = df['c'] * vrs
            for threshold in sorted(self.thresh_ws[key]):
                df['weibull'] = df.apply(lambda row: weibull_f(threshold, row['p'], 
                    row['v'], row['k']), axis=1)
                thresh_exceed[key].append(df['weibull'].sum())
        return sum(thresh_exceed.values(), [])