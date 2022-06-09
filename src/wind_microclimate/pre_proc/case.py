import os, math
import pandas as pd
from PyFoam.RunDictionary.ParameterFile import ParameterFile
from logging import info, warning, error, exception

from pre_proc import PreProc


class Case(PreProc):

    def __init__(self, preproc_obj, wind_profile, angle):
        self.__dict__ = preproc_obj.__dict__
        self.angle = angle
        self.case = f'{self.template_case}_{self.angle}'
        self.wind_profile = wind_profile


    def setup_case(self):
        """ Copy the template case and prepare it for calculation of current 
            wind direction. """

        self.template_case.cloneCase(self.case)
        self.wind_vector = [-math.sin(self.angle/180. * math.pi), 
            -math.cos(self.angle/180. * math.pi)]
        # custom csv wind profile setup
        if self.wind_profile == 'csv':
            self.write_vel_prof(self.csv_profile)
        # logarithmic ABL wind profile setup
        elif self.wind_profile == 'log':
            self.set_dir()
        outlets = self.choose_outlet()
        info(f'Preparing case for {self.angle} deg wind direction...',
            f'\nSetting patches: {outlets} to pressure outlet...'
            f'\nFlow direction vector: {self.wind_vector}')
        for outlet in outlets:
            self.set_outlet(outlet)


    def set_dir(self):
        """ Set wind direction vector """

        wind_dir = ParameterFile(os.path.join(self.case, '0', 'include', 
            'windDirection'))
        wind_dir.replaceParameter('flowDir', f'({self.wind_vector[0]}',
            f'{self.wind_vector[1]} 0)')


    def set_outlet(self, outlet_patch):
        """ Assign outlet BC to a given patch for all fields provided """

        for field in self.fields:
            path = os.path.join(self.case, '0', field)
            lineNr = 0
            with open(path) as f:
                i = 0
                for line in f:
                    i += 1
                    if outlet_patch in line:
                        lineNr = i
            with open(path) as r:
                lineList = r.readlines()
                lineList[lineNr+1] = f'#include "include/{field}Outlet"\n'
            with open(path, 'w') as mf:
                mf.writelines(lineList)


    def choose_outlet(self):
        """ Choose outlet boundary from the dictionary based on a given angle"""

        for key in sorted(self.outlet_dict):
            if self.angle <= key:
                return self.outlet_dict[key]


    def write_vel_prof(self, csv_path):
        """ Calculate the velocity profile based on given wind direction 
            and write to csv """

        cols = ['z', 'vx', 'vy', 'vz']
        df_vel = pd.read_csv(csv_path, header=None, names=cols)
        df_vel['vx'] = df_vel['vx'] * self.wind_vector[0]
        df_vel['vy'] = df_vel['vy'] * self.wind_vector[1]
        df_vel.to_csv(os.path.join(self.case, csv_path), header=False, index=False)
