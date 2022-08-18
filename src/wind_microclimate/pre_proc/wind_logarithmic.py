import os, math, glob
from PyFoam.RunDictionary.ParameterFile import ParameterFile
from scipy.integrate import quad
from logging import info

from wind_microclimate.pre_proc.case import Case


class WindLogarithmic(Case):
    
    def __init__(self, case_path: str, rht_epw: float, rht_site: float,
                 z_ground: float, v_ref: float, angle=0):
        super().__init__(case_path, angle=angle)
        self.rht_epw = rht_epw
        self.rht_site = rht_site
        self.z_ground = z_ground
        self.v_ref = v_ref

    def setup_template(self, output_dir, h_max=500):
        """ Prepare the template case with logarithmic wind profile setup """
        info(f'Yearly average wind speed from weather file is: ' +
             f'{str(round(self.v_ref, 2))} m/s')
        # wind profile scaling (from measurement station to site location)
        self.vref_site = self.calc_vref(h_max=h_max)
        info(f'Reference velocity used for applying the atmospheric wind ' +
             f'profile is: {str(round(self.vref_site, 2))} m/s')
        # write text file with wind profile parameters for site location
        self.write_profile_params(output_dir)
        # sets wind profile inputs
        self.set_ABL()
    
    def calc_vref(self, z_ref=10, h_max=500, step=0.01):
        """ Wind profile scaling - calculation of reference wind speed for the 
        site of interest based on the wind profile for measurement station and 
        surface roughness for the site of interest """
        integrate = lambda func, a, b, f_args: \
                        quad(func, a, b, args=f_args)[0]
        log_profile_func = lambda z, rht, vref: \
                        vref * math.log(z/rht) / math.log(z_ref/rht)

        ref_profile_ave = integrate(log_profile_func, 0, h_max, (self.rht_epw, 
            self.v_ref))/h_max
        error = ref_profile_ave
        i = 0
        while abs(error) > step:
            vref_site = self.v_ref - i * step
            integral_site = integrate(log_profile_func, 0, h_max, (self.rht_site,
                vref_site))
            site_profile_ave = integral_site/h_max
            error = ref_profile_ave - site_profile_ave
            i += 1
        return vref_site

    def set_ABL(self):
        """ Set parameters (z0/rht and v_ref) for the atmospheric boundary layer 
            profile"""
        # if OpenFOAM version < 6 then choose ABLprofile_5 for setup
        if self.version < 6:
            self.choose_file(os.path.join(self.incl_dir, 'ABLprofile'), 5)
        # if OpenFOAM version >= 6 then choose ABLprofile_6 for setup
        else:
            self.choose_file(os.path.join(self.incl_dir, 'ABLprofile'), 6)

        log_profile = ParameterFile(os.path.join(self.incl_dir, 'ABLprofile'))
        log_profile.replaceParameter('z0', 'uniform {0}'.format(self.rht_site))
        log_profile.replaceParameter('zGround', 'uniform {0}'.format(self.z_ground))
        log_profile.replaceParameter('Uref', self.vref_site)

    def write_profile_params(self, output_dir,
                             params_file='log-profile-parameters.txt'):
        """ Write parameters of the logarithmic wind profiles for both measurement 
        station and site of interest to a file """
        with open(os.path.join(output_dir, params_file), 'w') as f:
            f.write(f'measurement station reference velocity: {round(self.v_ref, 2)}')
            f.write(f'\nmeasurement station surface roughness: {self.rht_epw}')
            f.write(f'\nsite reference velocity: {round(self.vref_site, 2)}')
            f.write(f'\nsite surface roughness: {self.rht_site}')

    def set_wind(self):
        """ Set wind direction vector """
        # choose apropriate type of velocity inlet BC
        self.choose_file(os.path.join(self.incl_dir, 'UInlet'), 'log')

        wind_dir = ParameterFile(os.path.join(self.incl_dir, 'windDirection'))
        wind_dir.replaceParameter('flowDir', f'({self.wind_vector[0]} '
            + f'{self.wind_vector[1]} 0)')

    def return_clone(self, clone_path, angle):
        return WindLogarithmic(clone_path, self.rht_epw, self.rht_site,
                               self.z_ground, self.v_ref, angle=angle)
