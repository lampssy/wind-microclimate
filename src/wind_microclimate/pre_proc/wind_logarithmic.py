import os, math
from pathlib import Path
from PyFoam.RunDictionary.ParameterFile import ParameterFile
from scipy.integrate import quad
from logging import info

from pre_proc.case import Case


class WindLogarithmic(Case):
    
    def __init__(self, case_path: str, rht_epw: float, rht_site: float,
                 vref_epw: float, angle=0):
        super().__init__(case_path, angle=angle)
        self.rht_epw = rht_epw
        self.rht_site = rht_site
        self.vref_epw = vref_epw

    def setup_template(self, h_max=500):
        """ Prepare the template case with logarithmic wind profile setup """
        info(f'Yearly average wind speed from weather file is:', 
            f'{str(round(self.vref_epw, 2))} m/s')
        # wind profile scaling (from measurement station to site location)
        self.vref_site = self.calc_vref(h_max=h_max)
        info(f'Reference velocity used for applying the atmospheric wind profile',
             f'is: {str(round(self.vref_site, 2))} m/s')
        # write text file with wind profile parameters for site location
        self.write_profile_params()
        # sets wind profile inputs
        self.set_ABL()
    
    def calc_vref(self, z_ref=10, h_max=500, step=0.01):
        """ Wind profile scaling - calculation of reference wind speed for the 
        site of interest based on the wind profile for measurement station and 
        surface roughness for the site of interest """
        integrate = lambda func, a, b, f_args: \
                        quad(func, a, b, args=f_args)[0]
        log_profile_func = lambda vref, z, rht: \
                        vref * math.log(z/rht) / math.log(z_ref/rht)

        ref_profile_ave = integrate(log_profile_func, 0, h_max, (self.rht_epw, 
            self.vref_epw))/h_max
        error = ref_profile_ave
        i = 0
        while abs(error) > step:
            vref_site = self.vref_epw - i * step
            integral_site = integrate(log_profile_func, (self.rht_site, 
                vref_site))
            site_profile_ave = integral_site/h_max
            error = ref_profile_ave - site_profile_ave
            i += 1
        return vref_site

    def set_ABL(self):
        """ Set parameters (z0/rht and v_ref) for the atmospheric boundary layer 
            profile"""
        log_profile = ParameterFile(os.path.join(self.case_path, '0', 'include', 
            'ABLprofile'))
        log_profile.replaceParameter('z0', 'uniform {0}'.format(self.rht_site))
        log_profile.replaceParameter('Uref', self.vref_site)

    def write_profile_params(self, params_file='log-profile-parameters.txt'):
        """ Write parameters of the logarithmic wind profiles for both measurement 
        station and site of interest to a file """
        with open(params_file, 'w') as f:
            f.write(f'measurement station reference velocity: {self.vref_epw}')
            f.write(f'\nmeasurement station surface roughness: {self.rht_epw}')
            f.write(f'\nsite reference velocity: {self.vref_site}')
            f.write(f'\n sitesurface roughness: {self.rht_site}')

    def set_wind(self):
        """ Set wind direction vector """
        wind_dir = ParameterFile(os.path.join(self.case_path, '0', 'include', 
            'windDirection'))
        wind_dir.replaceParameter('flowDir', f'({self.wind_vector[0]}',
            f'{self.wind_vector[1]} 0)')

    def clone(self, clone_dir, angle):
        clone_path = Path(clone_dir, os.path.split(self.case_path)[1]
                          + f'_{angle}')
        self.foam_obj.cloneCase(clone_path)
        return WindLogarithmic(clone_path, self.rht_epw, self.rht_site,
                               self.vref_epw, angle=angle)
