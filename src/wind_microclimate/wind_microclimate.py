import os, sys, logging
import numpy as np
from pathlib import Path

from wind_microclimate.input.user_input import UserInput
from wind_microclimate.weather.epw import EpwWeatherData
from wind_microclimate.weather.weibull import WeibullWeatherData
from wind_microclimate.pre_proc.wind_csv import WindCSV
from wind_microclimate.pre_proc.wind_logarithmic import WindLogarithmic
from wind_microclimate.solver.solver import Solver
from wind_microclimate.post_proc.helpers import postproc_background
from wind_microclimate.post_proc.vr import VR
from wind_microclimate.post_proc.lawson_epw import LawsonEpw
from wind_microclimate.post_proc.lawson_weibull import LawsonWeibull


def main():
    ########################## INPUT & PATH NAMES #############################
    
    project_dir = Path(sys.argv[1])
    # main input/output paths
    input_dir = project_dir / 'input'
    output_dir = project_dir / 'output'

    # create output_dir if not exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # logging directory
    logfile = output_dir / 'wind_microclimate.log'
    Path(os.path.dirname(logfile)).mkdir(parents=True, exist_ok=True)

    # logging configuration
    logging.getLogger(__name__)
    logging.basicConfig(filename=logfile, level=logging.INFO,
                        format='%(asctime)s: %(levelname)s: %(message)s',
                        datefmt="%Y-%m-%d %H:%M:%S")

    # specific input paths
    input_xlsx = input_dir / 'INPUT.xlsx'
    inputs = UserInput(input_xlsx)
    input_case = input_dir / inputs.case
    hist_weather_data = input_dir / 'Heathrow 1997-01-01 to 2016-12-31.csv'
    
    # application will write paraview settings to this file
    pv_input = input_dir / 'pv_input.txt'

    # specific output paths
    output_weather = output_dir / 'weibull_fit'
    output_solver = output_dir / 'solver'
    output_vr = output_dir / 'VR'
    output_lawson = output_dir / 'lawson'
    csv_vr = output_vr / 'VR.csv'
    csv_lawson = output_lawson / 'lawson.csv'

    # wind angles to be assessed
    angles = np.linspace(inputs.angle_start, inputs.angle_end, 
                         num=inputs.angles, endpoint=True)

    # check if any post-processing action will be executed
    post_process = any([inputs.vr_calculate, inputs.vr_pictures,
                       inputs.vr_receptors, inputs.lawson_calculate,
                       inputs.lawson_pictures, inputs.lawson_receptors])
    if post_process:
        # write paraview inputs to the file
        inputs.write_pv_input(pv_input)

    #################### PRE-PROCESSING & CALCULATION #########################

    if inputs.run_cfd:
        # create case object that will be used as a template
        # template steup depends on the provided wind profile type - csv or log
        if inputs.wind_profile == 'csv':
            case_template = WindCSV(input_case, input_dir / inputs.csv_profile,
                                    inputs.z_ground, inputs.weibull_vref)
        else:
            wtr = EpwWeatherData(input_dir)
            case_template = WindLogarithmic(input_case, inputs.rht_epw,
                                            inputs.rht_site, inputs.z_ground,
                                            wtr.v_ref)

        # convert Fluent msh file to OpenFoam mesh
        if inputs.convert_msh:
            case_template.prepare_mesh(input_dir)

        case_template.setup_template(output_dir)

        for angle in angles:
            # clone template case to create case for current wind angle
            case = case_template.clone(output_solver, angle)
            case.setup_case()

            # create solver object for CFD calculation
            sol = Solver(case, inputs.proc, inputs.it, save_residuals=True)
            sol.calculate_cfd()

            # initiate post-processing activities in the background
            p = postproc_background(sol.case, sol.iterations, csv_vr, output_vr,
                pv_input, logfile, vr_pictures=inputs.vr_pictures, 
                vr_receptors=inputs.vr_receptors)

    ########################### POST-PROCESSING ###############################

    if post_process:
        # wait for the postproc_background to finish
        if inputs.run_cfd:
            logging.info(f'Waiting until post-processing of {case.case_path}' +
                         ' finishes')
            p.join()

        # create VR post-processing object
        vr = VR(output_solver, inputs.case, angles, csv_vr, output_vr)

        # create weather data and Lawson post-processing objects
        if inputs.method == 'weibull':
            wtr = WeibullWeatherData(hist_weather_data, inputs.weibull_vref,
                                     angles, input_dir, plot=True,
                                     plot_dir=output_weather)
            lawson = LawsonWeibull(output_solver, inputs.case, angles, wtr,
                                   inputs.prep_weibull_params, csv_vr,
                                   csv_lawson, inputs.lawson_receptors)
        if inputs.method == 'epw':
            if 'wtr' not in locals():
                wtr = EpwWeatherData(input_dir)
            lawson = LawsonEpw(output_solver, inputs.case, angles, wtr, csv_vr,
                               csv_lawson, inputs.lawson_receptors)

        # velocity ratio results
        if inputs.vr_calculate or inputs.vr_pictures or inputs.vr_receptors:
            vr.generate_results(inputs.vr_calculate, inputs.vr_receptors,
                                wtr.v_ref, pv_input, logfile=logfile)

        # calculate wind microclimate results
        if inputs.lawson_calculate:
            lawson.calculate()

        # calculate wind microclimate results in receptor locations
        if inputs.lawson_receptors:
            lawson.calculate(receptors=True)

        # generate colour maps with wind microclimate results
        if inputs.lawson_pictures:
            lawson.colour_map(pv_input, logfile=logfile)


if __name__ == '__main__':
    print('test')
    main()
