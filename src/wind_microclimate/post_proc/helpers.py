import os, subprocess, multiprocessing, re


def postproc_background(case, it, path_vr, output_vr, pv_input, logfile,
        vr_pictures=False, vr_receptors=False, vr_script='pv_vr.py',
        path_vr_receptors='lawson_receptors.csv'):
    """ Reconstruct, convert to VTK and run VR calculation if not done already.
        This can be done in the background, so that the calculation of next 
        wind direction start straight away """
    # cleaning the directory from unnecessary files
    case.foam_obj.clearOther(pyfoam=True, removeAnalyzed=True)
    case_path = case.case_path
    commands = []
    if os.path.exists(os.path.join(case_path, str(it))) == False:
        commands.append(['reconstructPar', '-case', case_path, '-latestTime']) 
    if os.path.exists(os.path.join(case_path, 'VTK', '{0}_{1}.vtk'
        .format(case_path, it))) == False:
        commands.append(['foamToVTK', '-case', case_path, '-latestTime'])
    if (vr_pictures and not os.path.exists(path_vr)) \
    or (vr_receptors and not os.path.exists(path_vr_receptors)):
        commands.append(['pvpython', vr_script, case_path, case.v_ref,
                         output_vr, pv_input, logfile])
    p = multiprocessing.Process(target=init_sbp, args=(commands, case_path, ),)
    p.start()
    return p


def init_sbp(commands, case_path):
    for cmd in commands:
        with open(os.path.join(case_path, '{0}.log'.format(cmd[0])), 'w') as f:
            subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT)