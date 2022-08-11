import sys, logging
import numpy as np
from pathlib import Path

from input.user_input import UserInput
from weather.epw import EpwWeatherData
from weather.weibull import WeibullWeatherData
from pre_proc.wind_csv import WindCSV
from pre_proc.wind_logarithmic import WindLogarithmic
from solver.solver import Solver
from post_proc.helpers import postproc_background
from post_proc.vr import VR
from post_proc.lawson_epw import LawsonEpw
from post_proc.lawson_weibull import LawsonWeibull


def main():
    ########################## INPUT & PATH NAMES #############################
    
    project_dir = Path(sys.argv[1])
    
    # main input/output paths
    input_dir = project_dir / 'input'
    output_dir = project_dir / 'output'

    # logging configuration
    logging.basicConfig(filename=output_dir / 'log' / 'wind_microclimate.log', 
        level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

    # specific input paths
    input_xlsx = input_dir / 'input.xlsx'
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

    # create output_dir if not exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # wind angles to be assessed
    angles = np.linspace(inputs.angle_start, inputs.angle_end, 
                         num=inputs.angles, endpoint=False)

    # check if any post-processing action will be executed
    post_process = any([inputs.vr_calculate, inputs.vr_pictures,
                       inputs.vr_receptors, inputs.lawson_calculate,
                       inputs.lawson_pictures, inputs.lawson_receptors])

    #################### PRE-PROCESSING & CALCULATION #########################

    if inputs.run_cfd:
        # create case object that will be used as a template
        # template steup depends on the provided wind profile type - csv or log
        if inputs.wind_profile == 'csv':
            case_template = WindCSV(input_case, input_dir / inputs.csv_profile)
        else:
            wtr = EpwWeatherData()
            case_template = WindLogarithmic(input_case, inputs.rht_epw,
                                            inputs.rht_site, wtr.v_ref)

        # convert Fluent msh file to OpenFoam mesh
        if inputs.convert_msh:
            case_template.prepare_mesh(input_dir)

        case_template.setup_template()

        for angle in angles:
            # clone template case to create case for current wind angle
            case = case_template.clone(output_solver, angle)
            case.setup_case()

            # create solver object for CFD calculation
            sol = Solver(case, inputs.proc, inputs.it, save_residuals=True)
            sol.calculate_cfd()

            # initiate post-processing activities in the background
            postproc_background(sol.case.foam_obj, sol.iterations, csv_vr, 
                                vr_pictures=inputs.vr_pictures, 
                                vr_receptors=inputs.vr_receptors)

    ########################### POST-PROCESSING ###############################

    if post_process:
        # write paraview inputs to the file
        inputs.write_pv_input(pv_input)

        # create VR post-processing object
        vr = VR(output_solver, inputs.case, angles, csv_vr, output_vr)

        # create weather data and Lawson post-processing objects
        if inputs.method == 'weibull':
            wtr = WeibullWeatherData(hist_weather_data, inputs.weibull_vref,
                                     angles, input_dir, plot=True,
                                     plot_dir=output_weather)
            lawson = LawsonWeibull(output_solver, inputs.case, angles, wtr,
                                   csv_vr, csv_lawson, inputs.lawson_receptors)
        if inputs.method == 'epw' and 'wtr' not in locals():
            wtr = EpwWeatherData()
            lawson = LawsonEpw(output_solver, inputs.case, angles, wtr, csv_vr,
                               csv_lawson, inputs.lawson_receptors)

        # velocity ratio results
        if inputs.vr_calculate or inputs.vr_pictures or inputs.vr_receptors:
            vr.generate_results(inputs.vr_calculate, inputs.vr_receptors,
                                wtr.v_ref, pv_input)

        # calculate wind microclimate results
        if inputs.lawson_calculate:
            lawson.calculate()

        # calculate wind microclimate results in receptor locations
        if inputs.lawson_receptors:
            lawson.calculate(receptors=True)

        # generate colour maps with wind microclimate results
        if inputs.lawson_pictures:
            lawson.colour_map(pv_input)


if __name__ == '__main__':
    main()
