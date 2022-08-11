import json, sys
import pandas as pd
from logging import info, error, exception


class UserInput:

    def __init__(self, input_file):
        info(f'Reading inputs from file {input_file}...')
        try:
            self.inputs = pd.read_excel(input_file, index_col=0)
        except FileNotFoundError:
            exception(f'{input_file} file not found')
        self.basic_input()
        self.pre_proc_input()
        self.solver_input()
        self.post_proc_input()

    def basic_input(self):
        self.case = self.inputs.loc['case', 'INPUT VALUE']
        self.angles = self.inputs.loc['wind_angles', 'INPUT VALUE']
        self.angle_start = self.inputs.loc['wind_angle_start', 'INPUT VALUE']
        self.angle_end = self.inputs.loc['wind_angle_end', 'INPUT VALUE']

    def pre_proc_input(self):
        self.convert_msh = self.inputs.loc['convert_mesh', 'INPUT VALUE']
        self.wind_profile = self.inputs.loc['wind_profile', 'INPUT VALUE']
        if self.wind_profile == 'csv':
            self.csv_profile = self.inputs.loc['csv_profile', 'INPUT VALUE'] 
        elif self.wind_profile == 'logarithmic':
            self.rht_epw = self.inputs.loc['rht_epw', 'INPUT VALUE']
            self.rht_site = self.inputs.loc['rht_site', 'INPUT VALUE']
        else:
            error(f'{self.wind_profile} wind profile not valid, available \
                  options are:\ncsv\nlogarithmic')
            sys.exit()

    def solver_input(self):
        self.run_cfd = self.inputs.loc['run_cfd', 'INPUT VALUE']
        self.proc = self.inputs.loc['processors', 'INPUT VALUE']
        self.it = self.inputs.loc['iter', 'INPUT VALUE']

    def post_proc_input(self):
        self.vr_calculate = self.inputs.loc['vr_calculate', 'INPUT VALUE']
        self.vr_pictures = self.inputs.loc['vr_pictures', 'INPUT VALUE']
        self.vr_receptors = self.inputs.loc['vr_receptors', 'INPUT VALUE']
        self.lawson_calculate = self.inputs.loc['lawson_calculate', 'INPUT VALUE']
        self.lawson_pictures = self.inputs.loc['lawson_pictures', 'INPUT VALUE']
        self.lawson_receptors = self.inputs.loc['lawson_receptors', 'INPUT VALUE']

        if self.vr_calculate or self.vr_pictures:
            self.vr_surfaces = self.inputs.loc['vr_surfaces', 'INPUT VALUE']
        if self.vr_receptors:
            self.receptors_csv = self.inputs.loc['receptor_coords', 'INPUT VALUE']
        if self.lawson_calculate or self.lawson_receptors or self.lawson_pictures or \
                self.vr_calculate or self.vr_pictures or self.vr_receptors:
            self.method = self.inputs.loc['lawson_method', 'INPUT VALUE']
            if self.method != 'epw' and self.method != 'weibull':
                error(f'{self.method} method is not valid for wind \
                      microclimate calculation')
                sys.exit()
            if self.method == 'weibull':
                self.weibull_vref = self.inputs.loc['weibull_vref', 'INPUT VALUE']
        if self.lawson_pictures:
            self.bld_of_interest = self.inputs.loc['bld_of_interest', 'INPUT VALUE']
            self.other_bld = self.inputs.loc['other_bld', 'INPUT VALUE']
        if self.vr_calculate or self.vr_pictures or self.lawson_pictures:
            self.x_camera = self.inputs.loc['x_camera', 'INPUT VALUE']
            self.y_camera = self.inputs.loc['y_camera', 'INPUT VALUE']
            self.h_ref = self.inputs.loc['h_ref', 'INPUT VALUE']

    def write_pv_input(self, path):
        paraview_rows = ['vr_calculate', 'vr_pictures', 'vr_receptors', 
            'vr_surfaces', 'receptor_coords', 'bld_of_interest', 'other_bld',
            'x_camera', 'y_camera', 'h_ref']
        self.inputs_paraview = self.inputs.loc[paraview_rows].to_dict()['INPUT VALUE']
        with open(path, 'w') as pv_input:
            pv_input.write(json.dumps(self.inputs_paraview, indent=0))
