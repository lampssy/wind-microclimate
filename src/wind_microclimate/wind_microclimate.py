import numpy as np

from input.user_input import UserInput
from weather.epw import EpwWeatherData
from weather.weibull import WeibullWeatherData
from pre_proc.pre_proc import PreProc
from solver.solver import Solver
from post_proc.post_proc import PostProc
from post_proc.helpers import postproc_background


def main():

    ################################# INPUT ###################################
    input_xlsx = 'input.xlsx'
    hist_weather_data = 'weibull_weather.csv'
    csv_vr = 'VR.csv'
    csv_lawson = 'lawson.csv'
    output_dir = 'output'

    inputs = UserInput(input_xlsx)

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
        pre = PreProc(inputs.case)
        if inputs.convert_msh:
            pre.convert_mesh()
        if inputs.wind_profile == 'csv':
            pre.setup_template_csv(inputs.csv_profile)
        else:
            wtr = EpwWeatherData()
            pre.setup_template_log(inputs.rht_epw, inputs.rht_site, wtr.v_ref)
        for angle in angles:
            pre.setup_case(angle)
            sol = Solver(pre.case, output_dir, inputs.proc, inputs.it, 
                         save_residuals=True)
            sol.calculate_cfd()
            # initiates post-processing activities in the background
            postproc_background(sol.case_obj, sol.iterations, csv_vr, 
                                vr_pictures=inputs.vr_pictures, 
                                vr_receptors=inputs.vr_receptors)

    ########################### POST-PROCESSING ###############################

    if post_process:
        # create weather data object for post-processing
        if weibull_weather:
            wtr = WeibullWeatherData(hist_weather_data, inputs.weibull_vref,
                                     plot=True)
        if  epw_weather and 'wtr' not in locals():
            wtr = EpwWeatherData()

        post = PostProc(inputs.case, angles, wtr, csv_vr, csv_lawson)

        # velocity ratio results
        if inputs.vr_calculate or inputs.vr_pictures or inputs.vr_receptors:
            post.vr_results(inputs.vr_calculate, inputs.vr_receptors, wtr.v_ref)

        # calculate wind microclimate results
        if inputs.lawson_calculate:
            post.lawson_calculate(inputs.method)

        # calculate wind microclimate results in receptor locations
        if inputs.lawson_receptors:
            post.lawson_calculate(inputs.method, receptors=True)

        # generate colour maps with wind microclimate results
        if inputs.lawson_pictures:
            post.lawson_pictures()


if __name__ == '__main__':
    main()
