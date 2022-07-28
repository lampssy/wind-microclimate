import sys
import numpy as np
from pathlib import Path

from input.user_input import UserInput
from weather.epw import EpwWeatherData
from weather.weibull import WeibullWeatherData
from pre_proc.wind_csv import WindCSV
from pre_proc.wind_logarithmic import WindLogarithmic
from solver.solver import Solver
from post_proc.vr import VR
from post_proc.helpers import postproc_background
from wind_microclimate.post_proc.lawson import LawsonLDDC


def main():
    ################################# INPUT ###################################
    
    project_dir = Path(sys.argv[1])
    
    input_dir = project_dir / 'input'
    output_dir = project_dir / 'output'

    input_xlsx = input_dir / 'input.xlsx'
    hist_weather_data = input_dir / 'weibull_weather.csv'

    Path(project_dir / output_dir).mkdir(parents=True, exist_ok=True)
    csv_vr = output_dir / 'VR' / 'VR.csv'
    csv_lawson = output_dir / 'lawson' / 'lawson.csv'
    
    inputs = UserInput(input_xlsx)

    input_case = input_dir / inputs.case

    angles = np.linspace(inputs.angle_start, inputs.angle_end, 
                         num=inputs.angles, endpoint=False)

    post_process = any([inputs.vr_calculate, inputs.vr_pictures,
                       inputs.vr_receptors, inputs.lawson_calculate,
                       inputs.lawson_pictures, inputs.lawson_receptors])

    weibull_weather = inputs.method == 'weibull' \
                      and any([inputs.lawson_calculate, inputs.lawson_receptors])

    epw_weather = inputs.method == 'epw' \
                  and any([inputs.vr_calculate, inputs.vr_receptors, 
                  inputs.lawson_calculate, inputs.lawson_receptors])

    #################### PRE-PROCESSING & CALCULATION #########################

    if inputs.run_cfd:

        if inputs.wind_profile == 'csv':
            case_template = WindCSV(input_case, inputs.csv_profile)
        else:
            wtr = EpwWeatherData()
            case_template = WindLogarithmic(input_case, inputs.rht_epw,
                                            inputs.rht_site, wtr.v_ref)

        if inputs.convert_msh:
            case_template.prepare_mesh(input_dir)

        case_template.setup_template()

        for angle in angles:

            case = case_template.clone(output_dir / 'solver', angle)
            case.setup_case()

            sol = Solver(case, inputs.proc, inputs.it, save_residuals=True)
            sol.calculate_cfd()

            # initiates post-processing activities in the background
            postproc_background(sol.case.foam_obj, sol.iterations, csv_vr, 
                                vr_pictures=inputs.vr_pictures, 
                                vr_receptors=inputs.vr_receptors)

    ########################### POST-PROCESSING ###############################

    if post_process:
        # create weather data object for post-processing
        if weibull_weather:
            wtr = WeibullWeatherData(hist_weather_data, inputs.weibull_vref,
                                     plot=True)
        if epw_weather and 'wtr' not in locals():
            wtr = EpwWeatherData()

        # create objects for VR and wind comfort categories post-processing
        vr = VR(inputs.case, angles, csv_vr, output_dir / 'VR')
        lawson = LawsonLDDC(inputs.case, angles, wtr, csv_vr, csv_lawson,
                            inputs.lawson_receptors)

        # velocity ratio results
        if inputs.vr_calculate or inputs.vr_pictures or inputs.vr_receptors:
            vr.generate_results(inputs.vr_calculate, inputs.vr_receptors,
                                wtr.v_ref)

        # calculate wind microclimate results
        if inputs.lawson_calculate:
            lawson.calculate()

        # calculate wind microclimate results in receptor locations
        if inputs.lawson_receptors:
            lawson.calculate(receptors=True)

        # generate colour maps with wind microclimate results
        if inputs.lawson_pictures:
            lawson.colour_map()


if __name__ == '__main__':
    main()
