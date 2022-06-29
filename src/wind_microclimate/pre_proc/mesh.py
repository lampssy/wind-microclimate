import os, sys, glob, multiprocessing
from PyFoam.Applications.Runner import Runner
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from logging import info, warning, error, exception

from post_proc import helpers
import pre_proc.pre_proc as pre

class Mesh(pre.PreProc):

    def __init__(self, preproc_obj):
        self.__dict__ = preproc_obj.__dict__
        if os.path.exists(os.path.join(self.template_case, 'constant')) == False:
            error(f'There is no "constant" directory in {self.template_case}')
            sys.exit()
        msh_list = glob.glob('*.msh')
        if len(msh_list) == 0:
            error('There is no msh file in project directory')
            sys.exit()
        elif len(msh_list) > 1:
            if any('_clean' in msh for msh in msh_list):
                info('Mesh already cleaned')
            else:
                error('There is more than one msh file in project directory')
                sys.exit()
        else:
            self.msh_file = msh_list[0]


    def prepare_mesh(self):
        """ Execute all mesh preparation activities - cleaning, converting msh file, 
        setting default boundary types and renumbering (reordering cells for 
        computational speed optimization) """

        self.clean_msh()
        self.convert_msh()
        self.set_boundaries()
        self.read_bc()
        self.renumber_mesh()
        # write boundary conditions from scratch as they get affected during 
        # renumbering and a 'template case' syntax is disrupted
        self.write_bc()


    def clean_msh(self):
        """ Clean the msh file - since ANSYS v2021 the msh files contain characters 
            not readable by the fluent3DMeshToFoam application """

        info('Cleaning mesh file...')
        msh_clean = self.msh_file.replace('.msh', '_clean.msh')
        forbidden_characters = ['[', ']']
        with open(self.msh_file) as f:
            f_list = f.readlines()
        new_list = []
        for line in f_list:
            for character in forbidden_characters:
                line = line.replace(character, '')
            new_list.append(line)
        with open(msh_clean, 'w') as f_new:
            f_new.writelines(new_list)
        os.remove(self.msh_file)


    def convert_msh(self):
        """ Convert the Fluent's msh file to OpenFOAM files and run mesh check 
            in the background"""

        print('\n###    MESH CONVERSION STARTED    ###\n')
        Runner(args=['fluent3DMeshToFoam', '-case', self.template_case, '*.msh'])
        print('\n###    MESH CONVERSION ENDED    ###\n')
        checkMesh = [['checkMesh', '-case', self.template_case]]
        p = multiprocessing.Process(target=helpers.init_sbp, args=(checkMesh, 
            self.template_case, ),)
        p.start()


    def renumber_mesh(self):
        """ Mesh renumbering - reorder cells to improve computational efficiency """

        template_dir = SolutionDirectory(self.template_case)
        print('\n###    MESH RENUMBERING STARTED    ###\n')
        Runner(args=['renumberMesh', '-case', self.template_case, '-overwrite'])
        print('\n###    MESH RENUMBERING ENDED    ###\n')
        template_dir.clearOther(pyfoam=True, removeAnalyzed=True)