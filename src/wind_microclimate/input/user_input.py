import json
import pandas as pd
from logging import info, warning, error, exception


class UserInput:

    def __init__(self, input_file):
        info(f'\nReading inputs from file {input_file}...\n')
        try:
            self.inputs = pd.read_excel(input_file, index_col=0)
        except FileNotFoundError:
            exception(f'{input_file} file not found')
        self.basic_input()
        self.pre_proc_input()
        self.solver_input()
        self.post_proc_input()

    def basic_input(self):
        self.case = self.inputs.loc['case']
        self.angles = self.inputs.loc['wind_angles']
        self.angle_start = self.inputs.loc['wind_angle_start']
        self.angle_end = self.inputs.loc['wind_angle_end']

    def pre_proc_input(self):
        self.convert_msh = self.inputs.loc['convert_mesh']
        self.wind_profile = self.inputs.loc['wind_profile']
        if self.wind_profile == 'csv':
            self.csv_profile = self.inputs.loc['csv_profile'] 
        elif self.wind_profile == 'logarithmic':
            self.rht_epw = self.inputs.loc['rht_epw']
            self.rht_site = self.inputs.loc['rht_site']
        else:
            error(f'{self.wind_profile} wind profile not valid, available',
                  'options are:\ncsv\nlogarithmic')

    def solver_input(self):
        self.run_cfd = self.inputs.loc['run_cfd']
        self.proc = self.inputs.loc['processors']
        self.it = self.inputs.loc['iter']

    def post_proc_input(self):
        self.vr_calculate = self.inputs.loc['vr_calculate']
        self.vr_pictures = self.inputs.loc['vr_pictures']
        self.vr_receptors = self.inputs.loc['vr_receptors']
        self.lawson_calculate = self.inputs.loc['lawson_calculate']
        self.lawson_pictures = self.inputs.loc['lawson_pictures']
        self.lawson_receptors = self.inputs.loc['lawson_receptors']

        if self.vr_calculate or self.vr_pictures:
            self.vr_surfaces = self.inputs.loc['vr_surfaces']
        if self.vr_receptors:
            self.receptors_csv = self.inputs.loc['receptor_coords']
        if self.lawson_calculate or self.lawson_receptors or \
                self.vr_calculate or self.vr_receptors:
            self.method = self.inputs.loc['method']
            if self.method == 'weibull':
                self.weibull_vref = self.inputs.loc['weibull_vref']
        if self.lawson_pictures:
            self.bld_of_interest = self.inputs.loc['bld_of_interest']
            self.other_bld = self.inputs.loc['other_bld']
        if self.vr_calculate or self.vr_pictures or self.lawson_pictures:
            self.x_camera = self.inputs.loc['x_camera']
            self.y_camera = self.inputs.loc['y_camera']
            self.h_ref = self.inputs.loc['h_ref']

    def write_pv_input(self, path):
        paraview_rows = ['vr_calculate', 'vr_pictures', 'vr_receptors', 
            'vr_surfaces', 'receptor_coords', 'other_bld', 'x_camera', 
            'y_camera', 'h_ref']
        self.inputs_paraview = self.inputs[paraview_rows].to_dict()
        with open(path, 'w') as pv_input:
            pv_input.write(json.dumps(self.inputs_paraview, indent=0))
