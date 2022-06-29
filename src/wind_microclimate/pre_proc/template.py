import os, math
from PyFoam.RunDictionary.ParameterFile import ParameterFile
from scipy.integrate import quad
from logging import info, warning, error, exception

from pre_proc.pre_proc import PreProc


class TemplateCaseLog(PreProc):
    
    def __init__(self, preproc_obj, rht_epw, rht_site, vref_epw):
        self.__dict__ = preproc_obj.__dict__
        self.rht_epw = rht_epw
        self.rht_site = rht_site
        self.vref_epw = vref_epw
        self.params_file = 'log-profile-parameters.txt'


    def setup_template_logarithmic(self):
        """ Prepare the template case with logarithmic wind profile setup """

        info(f'Yearly average wind speed from weather file is:', 
            f'{str(round(self.vref_epw, 2))} m/s')
        # wind profile scaling (from measurement station to site location)
        h_max = 500
        self.vref_site = self.site_profile(h_max)
        info(f'Reference velocity used for applying the atmospheric wind profile',
            f'is: {str(round(self.vref_site, 2))} m/s')
        # write text file with wind profile parameters for site location
        self.write_profile_params(self.params_file, round(self.vref_site, 2), 
            self.rht_site, round(self.vref_epw, 2), self.rht_epw)
        # sets wind profile inputs
        self.set_ABL()

    
    def site_profile(self, h_max):
        """ Wind profile scaling - calculation of reference wind speed for the 
        site of interest based on the wind profile for measurement station and 
        surface roughness for the site of interest """

        integrate = lambda func, a, b, f_args: \
                        quad(func, a, b, args=f_args)[0]
        log_profile_func = lambda vref, z, rht: \
                        vref * math.log(z/rht) / math.log(10/rht)

        ref_profile_ave = integrate(log_profile_func, 0, h_max, (self.rht_epw, 
            self.vref_epw))/h_max
        error = ref_profile_ave
        i = 0
        while abs(error) > 0.01:
            vref_site = self.vref_epw - i * 0.01
            integral_site = integrate(log_profile_func, (self.rht_site, 
                vref_site))
            site_profile_ave = integral_site/h_max
            error = ref_profile_ave - site_profile_ave
            i += 1
        return vref_site


    def set_ABL(self):
        """ Set parameters (z0/rht and v_ref) for the atmospheric boundary layer 
            profile"""

        log_profile = ParameterFile(os.path.join(self.case, '0', 'include', 
            'ABLprofile'))
        log_profile.replaceParameter('z0', 'uniform {0}'.format(self.rht_site))
        log_profile.replaceParameter('Uref', self.vref_site)


    def write_profile_params(self, params_file):
        """ Write parameters of the logarithmic wind profiles for both measurement 
        station and site of interest to a file """

        with open(params_file, 'w') as f:
            f.write(f'measurement station reference velocity: {self.vref_epw}')
            f.write(f'\nmeasurement station surface roughness: {self.rht_epw}')
            f.write(f'\nsite reference velocity: {self.vref_site}')
            f.write(f'\n sitesurface roughness: {self.rht_site}')