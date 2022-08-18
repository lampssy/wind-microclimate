import os, sys, math, shutil
from pathlib import Path
from abc import ABC, abstractmethod
from PyFoam.RunDictionary.BoundaryDict import BoundaryDict
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from PyFoam import FoamInformation
from logging import info, error, warning

from wind_microclimate.pre_proc.mesh import Mesh


class Case(ABC):

    def __init__(self, case_path, angle=0):
        self.case_path = case_path
        self.foam_obj = SolutionDirectory(case_path, archive=None)
        self.angle = angle
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
        self.incl_dir = os.path.join(self.case_path, '0', 'include')
        self.check_case()
        self.check_version()
    
    def setup_case(self):
        """ Copy the template case and prepare it for calculation of current 
            wind direction. """
        self.wind_vector = [-math.sin(self.angle/180. * math.pi), 
            -math.cos(self.angle/180. * math.pi)]
        self.set_wind()
        outlets = self.choose_outlet()
        info(f'Preparing case for {self.angle} deg wind direction... ' +
             f'\n\tSetting patches: {outlets} to pressure outlet... ' +
             f'\n\tFlow direction vector: {self.wind_vector}')
        for outlet in outlets:
            self.set_outlet(outlet)

    def prepare_mesh(self, msh_dir):
        """ Execute all mesh preparation activities - cleaning, converting msh file, 
        setting default boundary types and renumbering (reordering cells for 
        computational speed optimization) """
        self.mesh = Mesh(msh_dir, self.case_path)
        if self.mesh.cleaned:
            info('Mesh already cleaned')
        else:
            self.mesh.clean_msh()
        self.mesh.convert_msh()
        self.set_boundaries()
        self.read_bc()
        self.mesh.renumber_mesh()
        # write boundary conditions from scratch as they get affected during 
        # renumbering and a 'template case' syntax is disrupted
        self.write_bc()

    def set_outlet(self, outlet_patch):
        """ Assign outlet BC to a given patch for all fields provided """
        for field in self.fields:
            path = os.path.join(self.case_path, '0', field)
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

    def choose_file(self, file_path, suffix):
        shutil.copyfile(f'{file_path}_{suffix}', file_path)

    def read_bc(self):
        """ Read boundary condition files stored in "0" directory """
        fields = next(os.walk(os.path.join(self.case_path, '0')))[2]
        self.fields_dict = {}
        for field in fields:
            with open(os.path.join(self.case_path, '0', field), 'r') as f:
                self.fields_dict[field] = f.readlines()

    def write_bc(self):
        """ Write boundary condition files to "0" directory """
        fields = next(os.walk(os.path.join(self.case_path, '0')))[2]
        for field in fields:
            with open(os.path.join(self.case_path, '0', field), 'w') as f:
                f.writelines(self.fields_dict[field])

    def set_boundaries(self):
        """ Set standard boundary types: 'sky' to symmetry; 'side-n', 'side-e',
            'side-s', 'side-w' to patches; remaining to wall. """
        boundary_dict = BoundaryDict(self.case_path)
        patches = boundary_dict.patches()
        boundary_dict['sky']['type'] = 'symmetry'
        boundary_dict['sky']['inGroups'] = ['symmetry']
        for patch in patches:
            if patch != 'side-n' and patch != 'side-e' and patch != 'side-s' \
                and patch != 'side-w' and patch != 'sky':
                boundary_dict[patch]['type'] = 'wall'
                boundary_dict[patch]['inGroups'] = ['wall']
        boundary_dict.writeFile()

    def check_case(self):
        """ Check whether this is a valid case directory by looking for
            the system and constant directories and the controlDict file """
        if self.foam_obj.isValid() == False:
            error(f'There is no "constant" directory in {self.case_path}')
            sys.exit()

    def clone(self, clone_dir, angle):
        """ Clone case into clone_dir and return the resultant Case object.
            Skip cloning if such path exists and is a valid case directory """
        clone_path = str(Path(clone_dir, os.path.split(self.case_path)[1]
                          + f'_{angle}'))
        if not os.path.exists(clone_path) \
                or (os.path.exists(clone_path) \
                    and not SolutionDirectory(clone_path).isValid()):
            info(f'Creating case {clone_path}...')
            Path(clone_path).mkdir(parents=True, exist_ok=True)
            self.foam_obj.cloneCase(clone_path)
        return self.return_clone(clone_path, angle)

    def check_version(self):
        self.version = float(FoamInformation.foamVersionString())
        if not (5 <= self.version <= 8):
            warning(f'This application has been tested with versions ' +
                    f'5.0 - 8.0, your version (OpenFOAM {self.version}) '+
                    'may not be compatible')

    @abstractmethod
    def return_clone(clone_path, angle):
        pass

    @abstractmethod
    def set_wind(self):
        pass

    @abstractmethod
    def setup_template(self):
        pass
