import os, subprocess, time
from pathlib import Path
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from PyFoam.Applications.Decomposer import Decomposer
from PyFoam.Applications.PlotRunner import PlotRunner
from PyFoam import FoamInformation
from logging import warning


class Solver:

    def __init__(self, case, processors, iterations, save_residuals=False):
        self.case = case
        self.processors = processors
        self.iterations = iterations
        self.calculated = self.is_calculated()
        self.solver_args = [f'--procnr={self.processors}', '--no-pickled-file',
                        '--no-continuity', '--non-persist', 'simpleFoam', 
                        '-case', self.case.case_path]
        self.save_residuals = save_residuals
        if self.save_residuals:
            self.solver_args.insert(1, '--hardcopy')
            self.resid_dir = os.path.join(os.path.dirname(self.case.case_path),
                                          'residuals')

    def calculate_cfd(self):
        if not self.calculated:
            self.decompose()
            self.set_iter()
            self.run_simulation()

    def run_simulation(self):
        PlotRunner(args=self.solver_args)
        if self.save_residuals:
            self.residuals_plot()

    def decompose(self):
        """ Check if case decomposed to provided number of processors, 
            then decompose if not """
        print(self.processors)
        if self.case.foam_obj.nrProcs() != self.processors:
            if self.case.foam_obj.nrProcs() != 0:
                subprocess.run(['reconstructPar', '-case', self.case.case_path, 
                    '-latestTime'])
            Decomposer(args=[self.case.case_path, self.processors, '--clear'])


    def set_iter(self):
        conDict = ParsedParameterFile(os.path.join(self.case.case_path, 'system', 
            'controlDict'))
        conDict['endTime'] = self.iterations
        conDict.writeFile()

    def residuals_plot(self):
        Path(self.resid_dir).mkdir(parents=True, exist_ok=True)
        # make sure image with residuals has been created
        time.sleep(2)
        try:
            # PNG image of residuals
            subprocess.run(['mv', 'linear.png', os.path.join(self.resid_dir,
                f'residuals_{self.case.angle}.png')])
        except Exception:
            warning('Image with residuals was not generated')

    
    def is_calculated(self):
        if self.case.foam_obj.getLast() != self.iterations:
            return False
        else:
            return True

    def check_version(self):
        self.version = FoamInformation.foamVersionString()
        if not (5 <= float(self.version) <= 8):
            warning(f'This application has been tested with versions 5.0 - 8.0, \
                    your version (OpenFOAM {self.version}) may not be \
                    compatible')