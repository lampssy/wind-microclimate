import os, subprocess, glob
import pandas as pd


class VR:

    def __init__(self, case, angles, csv_vr, output_dir):
        self.case = case
        self.angles = angles
        self.csv_vr = csv_vr
        self.output_dir = output_dir

    def generate_results(self, vr_calculate, vr_receptors, vref):
        for angle in self.angles:
            case_name = f'{self.case}_{angle}'
            if os.path.exists(os.path.join(case_name, self.csv_vr)) == False:
                subprocess.run(['pvpython', 'pv_vr.py', case_name, vref, 
                    self.output_dir])
                if vr_calculate:
                    # merge CSV files with VR data for surfaces
                    self.merge_vr(self.csv_vr)
                if vr_receptors:
                    csv_vr_receptors = f'{self.csv_vr.rstrip(".csv")}' \
                                      + '_receptors.csv'
                    # merge CSV files with VR data for receptors
                    self.merge_vr(csv_vr_receptors)

    def merge_vr(self, path_merged):
        """ Merge csv files with VR results above individual surfaces into one
            csv file """
        csv_list = glob.glob(os.path.join(self.ca, '_VR*.csv'))
        dfs = [pd.read_csv(csv) for csv in csv_list]
        names = [csv.strip('_VR.csv') for csv in csv_list]
        for df, name in zip(dfs, names):
            df['Name'] = name
        df_concat = pd.concat(dfs)
        df_concat.to_csv(path_merged, index=False)
        # clean partial VR results in case folder
        for csv in csv_list:
            os.remove(csv)
