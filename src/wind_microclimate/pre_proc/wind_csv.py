import os
import pandas as pd
from pathlib import Path

from pre_proc.case import Case


class WindCSV(Case):
    
    def __init__(self, case_path: str, csv_profile: str, angle=0):
        super().__init__(case_path, angle=angle)
        self.csv_profile = csv_profile

    def set_wind(self):
        """ Calculate velocity profile based on thes given wind direction 
            and write to csv """
        csv_path = os.path.join(self.case_path, self.csv_profile)
        cols = ['z', 'vx', 'vy', 'vz']
        df_vel = pd.read_csv(csv_path, header=None, names=cols)
        df_vel['vx'] = df_vel['vx'] * self.wind_vector[0]
        df_vel['vy'] = df_vel['vy'] * self.wind_vector[1]
        df_vel.to_csv(os.path.join(self.case, csv_path), header=False,
                      index=False)

    def clone(self, clone_dir, angle):
        clone_path = Path(clone_dir, os.path.split(self.case_path)[1]
                          + f'_{angle}')
        self.foam_obj.cloneCase(clone_path)
        return WindCSV(clone_path, self.csv_profile, angle=angle)
