import glob
import multiprocessing
import os
import subprocess


def postproc_background(
    case,
    it,
    path_vr,
    output_vr,
    pv_input,
    logfile,
    vr_pictures=False,
    vr_receptors=False,
):
    """Reconstruct, convert to VTK and run VR calculation if not done already.
    This can be done in the background, so that the calculation of next
    wind direction start straight away"""
    clean_cwd()
    # cleaning the directory from unnecessary files
    case.foam_obj.clearOther(pyfoam=True, removeAnalyzed=True)
    case_path = case.case_path
    csv_vr = str(path_vr).replace('.csv', f'_{os.path.split(case_path)[1]}.csv')
    csv_vr_receptors = csv_vr.replace('VR_', 'VR_receptors_')
    commands = []
    if not os.path.exists(os.path.join(case_path, str(it))):
        commands.append(['reconstructPar', '-case', case_path, '-latestTime'])
    if not (
        os.path.exists(
            os.path.join(case_path, 'VTK', '{0}_{1}.vtk'.format(case_path, it))
        )
    ):
        commands.append(['foamToVTK', '-case', case_path, '-latestTime'])
    if (vr_pictures and not os.path.exists(csv_vr)) or (
        vr_receptors and not os.path.exists(csv_vr_receptors)
    ):
        commands.append(
            [
                'pvpython',
                vr_script,
                case_path,
                str(case.v_ref),
                output_vr,
                pv_input,
                logfile,
            ]
        )
    p = multiprocessing.Process(
        target=init_sbp,
        args=(
            commands,
            case_path,
        ),
    )
    p.start()
    return p


def init_sbp(commands, case_path):
    for cmd in commands:
        with open(os.path.join(case_path, '{0}.log'.format(cmd[0])), 'w') as f:
            subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT)


def clean_cwd():
    """Cluean current working directory from unwanted images of residuals
    after running simulations"""
    types = ['*bound*.png', '*linear*.png']
    files_grabbed = []
    for files in types:
        files_grabbed.extend(glob.glob(files))
    for f in files_grabbed:
        os.remove(f)


vr_script = str(os.path.join(os.path.split(__file__)[0], 'scripts', 'pv_vr.py'))
