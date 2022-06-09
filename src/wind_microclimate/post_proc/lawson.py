import math, string
import time
import numpy as np
import pandas as pd

from post_proc import PostProc


class LawsonLDDC(PostProc):

    def __init__(self, postproc_obj, receptors):
        self.__dict__ = postproc_obj.__dict__
        self.receptors = receptors
        self.thresh_ws = {
            'Comfort': [2.5, 4, 6, 8], 
            'Safety': [15]
            }
        self.thresh_freq = {
            'Comfort': [0.05, 0.05, 0.05, 0.05], 
            'Safety': [0.00022]
            }
        self.thresh_ws_values = sorted(sum(self.thresh_ws.values(), []),
            reverse=True)
        self.thresh_freq_values = sorted(sum(self.thresh_freq.values(), []), 
            reverse=True)


    def set_method(self, method):
        self.method = method.lower()
    

    def calculate(self):
        
        if self.method == 'weibull':
            self.wind_microclimate_weibull()
        else:
            self.wind_microclimate_epw()
            if self.method != 'epw':
                print(f'\nWARNING: {self.method} method is not valid for wind',
                'microclimate calculation, switching to epw as a default!',
                '\nAvailable methods: epw, weibull')


    def wind_microclimate_weibull(self, safety=True):
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
            self.lawson_classes(csv_lawson_season)


    def wind_microclimate_epw(self, safety=True):
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
            self.lawson_classes(self.csv_lawson)


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


    def lawson_classes(self, csv_lawson):
        """ Calculate exceedance of all threshold wind speeds using given method 
            (epw or weibull), assign relevant wind comfort class to each point 
            and write the results to a file """
    
        classes = np.zeros(len(self.dfs_vr[0]), dtype=float)
        for freq, idx in zip(self.p_exceed, range(classes.shape[0])):
            classes[idx] += self.assign_class(freq)
        classes[classes > len(self.thresh_ws_values) - 1] = \
            len(self.thresh_ws_values) - 1
        self.points_class = np.vstack((classes, 
                                    self.dfs_vr[0]['Points:0'].to_numpy(), 
                                    self.dfs_vr[0]['Points:1'].to_numpy(), 
                                    self.dfs_vr[0]['Points:2'].to_numpy())).T
        if not self.receptors:
            fields = 'Class,Points:0,Points:1,Points:2'
            np.savetxt(csv_lawson, self.points_class, delimiter=',', 
                fmt=['%d', '%f', '%f', '%f'], header=fields, comments='')
        else:
            self.receptors_table(csv_lawson)


    def assign_class(self, freq):
        """ Assign wind comfort class based on exceedance frequency of given 
            threshold wind speeds """

        assigned_class = len(self.thresh_freq_values)
        while freq[(assigned_class - 1)] \
            < self.thresh_freq_values[(assigned_class - 1)] \
            and assigned_class > 0:
            assigned_class -= 1
        return assigned_class


    def receptors_table(self, csv_lawson):
        """ Generate csv file with wind comfort results for receptor locations """

        print('Generating tabular wind comfort results for receptor locations...')
        names = self.dfs_vr[0]['Name']
        classes = np.delete(self.points_class, [1, 2, 3], 1)
        receptor_freq = np.concatenate((np.asarray(names), self.p_exceed*100), 
            axis=1)
        fields, fields_fmt = ['Name'], ['%s']
        class_dict = {}
        # add columns for exceedance of wind speed thresholds for each comfort class
        for key, value in zip(range(len(self.thresh_ws['Comfort']), 
                list(string.ascii_lowercase))):
            class_dict[key] = value
            fields.append(value)
            fields_fmt.append('%f')
        fields.append('Calculated class')
        fields_fmt.append('%s')
        # 'Uncomfortable/unsafe' comfort class
        class_dict[len(self.thresh_ws['Comfort']) + 1] = 'U'
        classes = np.vectorize(class_dict.get)(classes)
        receptor_table = np.concatenate((receptor_freq, classes), axis=1)
        csv_lawson_receptors = f'{csv_lawson.rstrip(".csv")}_receptors.csv'
        np.savetxt(csv_lawson_receptors, receptor_table, delimiter=',', 
            fmt=fields_fmt, header=fields, comments='')
