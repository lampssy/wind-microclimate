import os
import pandas as pd

from pre_proc.case import Case


class WindCSV(Case):
    
    def __init__(self, case_path: str, csv_path: str, v_ref, angle=0):
        super().__init__(case_path, angle=angle)
        self.csv_path = csv_path
        self.v_ref = v_ref

    def set_wind(self):
        """ Calculate velocity profile based on thes given wind direction
            and write to csv """
        df_vel = pd.read_csv(self.csv_path, header=None, names=['z', 'vel'])
        vel_prof = {'z': df_vel['z'],
                    'vx': df_vel['vel'] * self.wind_vector[0],
                    'vy': df_vel['vel'] * self.wind_vector[1],
                    'vz': [0] * len(df_vel['vel'])}
        df_prof = pd.DataFrame(vel_prof)
        df_prof.to_csv(os.path.join(self.case_path,
                                   os.path.split(self.csv_path)[1]),
                      header=False, index=False)

    def return_clone(self, clone_path, angle):
        return WindCSV(clone_path, self.csv_path, self.v_ref, angle=angle)

    def setup_template(self):
        pass
