from abc import ABC, abstractmethod
from pathlib import Path
import string, os, subprocess, glob
import numpy as np
import pandas as pd
from logging import info


class Lawson(ABC):

    def __init__(self, case_dir, case, angles, csv_vr, csv_lawson,
                 receptors):
        self.case = os.path.join(case_dir, case)
        self.angles = angles
        self.csv_vr = str(csv_vr)
        self.csv_vr_receptors = f'{self.csv_vr.rstrip(".csv")}_receptors.csv'
        self.csv_lawson = str(csv_lawson)
        self.p_exceed = np.zeros((2, 2)) # hack

    def calculate(self, receptors=False):
        """ Read VR data and initiate calculation of wind microclimate results 
            as per Lawson LDDC criteria. Exceedance of the wind speed thresholds 
            is calculated using one of the following methods: 
            - 'epw': exceedance during Typical Meteorological Year in epw file
            - 'weibull': using Weibull distribution parameters for a given location"""
        if receptors:
            csv_vr = self.csv_vr_receptors
        else:
            csv_vr = self.csv_vr
        # TO DO: check if dataframe is optimal for speed in this case
        self.dfs_vr = [pd.read_csv(csv_vr.replace
                       ('.csv', f'_{os.path.split(self.case)[1]}_{angle}.csv'),
                       header=0) for angle in self.angles]
        self.wind_microclimate(receptors=receptors)

    def calculate_classes(self, csv_lawson, receptors=False):
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
        Path(os.path.dirname(csv_lawson)).mkdir(parents=True, exist_ok=True)
        if not receptors:
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
        info('Generating tabular wind comfort results for receptor locations...')
        names = [[name] for name in self.dfs_vr[0]['Name']]
        classes = np.delete(self.points_class, [1, 2, 3], 1)
        receptor_freq = np.concatenate((np.asarray(names), self.p_exceed*100), 
            axis=1)
        fields, fields_fmt = ['Name'], ['%s']
        class_dict = {}
        n_thresholds = len(sum([val for val in self.thresh_ws.values()], []))
        # add columns for exceedance of wind speed thresholds for each comfort class
        for key, value in zip(range(n_thresholds), list(string.ascii_lowercase)):
            class_dict[key] = value
            fields.append(value)
            fields_fmt.append('%s')
        fields.append('Calculated class')
        fields_fmt.append('%s')
        # 'Uncomfortable/unsafe' comfort class
        class_dict[len(self.thresh_ws['Comfort']) + 1] = 'U'
        classes = np.vectorize(class_dict.get)(classes)
        receptor_table = np.concatenate((receptor_freq, classes), axis=1)
        csv_lawson_receptors = f'{csv_lawson.rstrip(".csv")}_receptors.csv'
        np.savetxt(csv_lawson_receptors, receptor_table, delimiter=',', 
            fmt=fields_fmt, header=','.join(fields), comments='')

    def colour_map(self, pv_input, logfile='pv_lawson.log'):
        lawson_script = str(os.path.join(os.path.split(__file__)[0], 'scripts',
                            'pv_lawson.py'))
        lawson_results_list = glob.glob(f'{self.csv_lawson.rstrip(".csv")}*.csv')
        for lawson_results in lawson_results_list:
            if 'receptors' not in lawson_results:
                subprocess.run(['pvpython', lawson_script, self.case, lawson_results,
                                pv_input, logfile])

    @abstractmethod
    def wind_microclimate(self):
        pass

    @property
    @abstractmethod
    def thresh_ws(self):
        pass

    @property
    @abstractmethod
    def thresh_freq(self):
        pass

    @property
    @abstractmethod
    def thresh_ws_values(self):
        pass

    @property
    @abstractmethod
    def thresh_freq_values(self):
        pass


class LawsonLDDC(Lawson):

    def __init__(self, case_dir, case, angles, csv_vr, csv_lawson, receptors):
        super().__init__(case_dir, case, angles, csv_vr, csv_lawson, receptors)

    @property
    def thresh_ws(self):
        return {
            'Comfort': [2.5, 4, 6, 8], 
            'Safety': [15]
            }

    @property
    def thresh_freq(self):
        return {
            'Comfort': [0.05, 0.05, 0.05, 0.05], 
            'Safety': [0.00022]
            }

    @property
    def thresh_ws_values(self):
        return sorted(sum(self.thresh_ws.values(), []), reverse=True)

    @property
    def thresh_freq_values(self):
        return sorted(sum(self.thresh_freq.values(), []), reverse=True)
