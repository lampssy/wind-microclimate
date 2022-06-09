import os, subprocess, glob
import pandas as pd

from post_proc import helpers
from lawson import LawsonLDDC

class PostProc:

    def __init__(self, case, angles, weather, csv_vr, csv_lawson, output_dir):
        self.case = case
        self.angles = angles
        self.weather = weather
        self.csv_vr = csv_vr
        self.csv_vr_receptors = f'{self.csv_vr.rstrip(".csv")}_receptors.csv'
        self.csv_lawson = csv_lawson
        self.output_dir = output_dir


    def vr_results(self, vr_calculate, vr_receptors, vref):
        for angle in self.angles:
            case_name = f'{self.case}_{angle}'
            if os.path.exists(os.path.join(case_name, self.csv_vr)) == False:
                subprocess.run(['pvpython', 'pv_vr.py', case_name, vref, 
                    self.output_dir])
                if vr_calculate:
                    # merge CSV files with VR data for surfaces
                    helpers.merge_vr(case_name, self.csv_vr)
                if vr_receptors:
                    # merge CSV files with VR data for receptors
                    helpers.merge_vr(case_name, self.csv_vr_receptors)


    def lawson_calculate(self, method, receptors=False):
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
        self.dfs_vr = [pd.read_csv(os.path.join(f'{self.case}_{angle}', csv_vr), 
            header=0, dtype=float) for angle in self.angles]
        # TO DO: check if this is efficient
        self.vr_gens = [(vr for vr in df_vr['VR'].tolist()) for df_vr in self.dfs_vr]
        
        lawson_results = LawsonLDDC(self, receptors)
        lawson_results.set_method(method)
        lawson_results.calculate()


    def lawson_pictures(self):
        lawson_results_list = glob.glob(f'{self.csv_lawson.rstrip(".csv")}*.csv')
        for lawson_results in lawson_results_list:
            subprocess.run(['pvpython', 'pv_lawson.py', lawson_results])