import os
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from PyFoam.RunDictionary.BoundaryDict import BoundaryDict

from pre_proc.mesh import Mesh
from pre_proc.template import TemplateCaseLog
from pre_proc.case import Case

class PreProc:

    def __init__(self, template_case):
        self.template_case = SolutionDirectory(template_case, archive=None)
        self.fields = ['U', 'p', 'k', 'epsilon']
        self.outlet_dict = {
            10: ['side-s'],
            80: ['side-s', 'side-w'],
            100: ['side-w'],
            170: ['side-w', 'side-n'],
            190: ['side-n'],
            260: ['side-n', 'side-e'],
            280: ['side-e'],
            350: ['side-e', 'side-s'],
            360: ['side-s']
            }


    def convert_mesh(self):
        mesh = Mesh(self)
        mesh.prepare_mesh()


    def setup_template_log(self, rht_epw, rht_site, vref_epw):
        self.wind_profile = 'log'
        template = TemplateCaseLog(self, rht_epw, rht_site, vref_epw)
        template.setup_logarithmic(rht_epw, rht_site)

    
    def setup_template_csv(self, csv_profile):
        self.wind_profile = 'csv'
        self.csv_profile = csv_profile


    def setup_case(self, angle):
        case = Case(self, angle)
        # set up the case if not done already
        if not os.path.exists(case.case):
            case.setup_case()
        self.case = SolutionDirectory(case.case)

    
    def set_boundaries(self):
        """ Set standard boundary types: 'sky' to symmetry; 'side-n', 'side-e', 
            'side-s', 'side-w' to patches; remaining to wall. """

        boundary_dict = BoundaryDict(self.template_case)
        patches = boundary_dict.patches()
        boundary_dict['sky']['type'] = 'symmetry'
        boundary_dict['sky']['inGroups'] = ['symmetry']
        for patch in patches:
            if patch != 'side-n' and patch != 'side-e' and patch != 'side-s' \
                and patch != 'side-w' and patch != 'sky':
                boundary_dict[patch]['type'] = 'wall'
                boundary_dict[patch]['inGroups'] = ['wall']
        boundary_dict.writeFile()


    def read_bc(self):
        """ Read boundary condition files stored in "0" directory """

        fields = next(os.walk(os.path.join(self.template_case, '0')))[2]
        self.fields_dict = {}
        for field in fields:
            with open(os.path.join(self.case, '0', field), 'r') as f:
                self.fields_dict[field] = f.readlines()


    def write_bc(self):
        """ Write boundary condition files to "0" directory """

        fields = next(os.walk(os.path.join(self.template_case, '0')))[2]
        for field in fields:
            with open(os.path.join(self.template_case, '0', field), 'w') as f:
                f.writelines(self.fields_dict[field])