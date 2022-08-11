import os, subprocess, glob
import pandas as pd
from pathlib import Path


class VR:

    def __init__(self, case_dir, case, angles, csv_vr, output_dir):
        self.case = str(os.path.join(case_dir, case))
        self.angles = angles
        self.csv_vr = str(csv_vr)
        self.output_dir = str(output_dir)

    def generate_results(self, vr_calculate, vr_receptors, vref, pv_input,
                         logfile='pv_vr.log'):
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        for angle in self.angles:
            case_name = f'{self.case}_{angle}'
            csv_vr_angle = self.csv_vr.replace('.csv',
                f'_{os.path.split(case_name)[1]}.csv')

            if (not vr_receptors and not os.path.exists(csv_vr_angle)) \
                    or (vr_receptors and not os.path.exists(csv_vr_angle \
                        .replace('.csv', '_receptors.csv'))):
                vr_script = str(os.path.join(os.path.split(__file__)[0],
                                'scripts', 'pv_vr.py'))
                subprocess.run(['pvpython', vr_script, case_name, str(vref),
                                self.output_dir, pv_input, logfile])
                if vr_calculate:
                    # merge CSV files with VR data for surfaces
                    self.merge_vr(case_name, csv_vr_angle)
                if vr_receptors:
                    # merge CSV files with VR data for receptors
                    self.merge_vr(case_name, csv_vr_angle.replace('.csv',
                                  '_receptors.csv'))

    def merge_vr(self, case, path_merged):
        """ Merge csv files with VR results above individual surfaces into one
            csv file """
        csv_list = glob.glob(os.path.join(case, '_VR*.csv'))
        print(case)
        dfs = [pd.read_csv(csv) for csv in csv_list]
        names = [os.path.split(csv.strip('_VR.csv'))[1] for csv in csv_list]
        for df, name in zip(dfs, names):
            df['Name'] = name
        df_concat = pd.concat(dfs)
        df_concat.to_csv(path_merged, index=False)
        # clean partial VR results in case folder
        for csv in csv_list:
            os.remove(csv)
