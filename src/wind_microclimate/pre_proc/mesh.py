import os, sys, glob, multiprocessing
from PyFoam.Applications.Runner import Runner
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from logging import info, error

from post_proc import helpers


class Mesh:

    def __init__(self, msh_dir, case_path):
        self.cleaned = False
        self.case_path = case_path
        self.find_msh(msh_dir)

    def find_msh(self, msh_dir):
        """ Find Fluent msh file in the given directory """
        msh_list = glob.glob(os.path.join(msh_dir, '*.msh'))
        if len(msh_list) == 0:
            error('There is no msh file in project directory')
            sys.exit()
        elif len(msh_list) > 1:
            error('There is more than one msh file in project directory')
            sys.exit()
        else:
            if '_clean' in msh_list[0]:
                self.cleaned = True
            self.msh_file = msh_list[0]

    def clean_msh(self, forbid_chars = ['[', ']']):
        """ Clean the msh file - ANSYS v2021 msh files contain characters
            ('['and ']') not readable by fluent3DMeshToFoam """
        info('Cleaning mesh file...')
        msh_clean = self.msh_file.replace('.msh', '_clean.msh')
        with open(self.msh_file) as f:
            f_list = f.readlines()
        new_list = []
        for line in f_list:
            for character in forbid_chars:
                line = line.replace(character, '')
            new_list.append(line)
        with open(msh_clean, 'w') as f_new:
            f_new.writelines(new_list)
        os.remove(self.msh_file)
        self.msh_file = msh_clean

    def convert_msh(self):
        """ Convert the Fluent's msh file to OpenFOAM files and run mesh check 
            in the background"""
        info('Converting the mesh from Fluent to OpenFOAM...')
        Runner(args=['fluent3DMeshToFoam', '-case', self.case_path,
                     self.msh_file])
        checkMesh = [['checkMesh', '-case', self.case_path]]
        p = multiprocessing.Process(target=helpers.init_sbp, args=(checkMesh, 
            self.case_path, ),)
        p.start()

    def renumber_mesh(self):
        """ Mesh renumbering - reorder cells to improve computational 
            efficiency"""
        template_dir = SolutionDirectory(self.case_path)
        info('Renumbering mesh cells...')
        Runner(args=['renumberMesh', '-case', self.case_path, '-overwrite'])
        template_dir.clearOther(pyfoam=True, removeAnalyzed=True)
