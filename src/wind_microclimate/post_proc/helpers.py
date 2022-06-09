import os, subprocess, multiprocessing, re, glob
import pandas as pd


def merge_vr(case, path_merged):
    """ Merge csv files with VR results above individual surfaces into one 
        csv file """

    csv_list = glob.glob(os.path.join(case, '_VR*.csv'))
    dfs = [pd.read_csv(csv) for csv in csv_list]
    names = [csv.strip('_VR.csv') for csv in csv_list]
    for df, name in zip(dfs, names):
        df['Name'] = name
    df_concat = pd.concat(dfs)
    df_concat.to_csv(path_merged, index=False)
    # clean partial VR results in case folder
    for csv in csv_list:
        os.remove(csv)


def postproc_background(case_obj, it, path_vr, vr_pictures=False, 
    vr_receptors=False, path_vr_receptors='lawson_receptors.csv'):
    """ Reconstruct, convert to VTK and run VR calculation if not done already. 
        This can be done in the background, so that the calculation of next 
        wind direction start straight away """

    # cleaning the directory from unnecessary files
    case_obj.clearOther(pyfoam=True, removeAnalyzed=True)
    case = case_obj.name
    commands = []
    if os.path.exists(os.path.join(case, str(it))) == False:
        commands.append(['reconstructPar', '-case', case, '-latestTime']) 
    if os.path.exists(os.path.join(case, 'VTK', '{0}_{1}.vtk'
        .format(case, it))) == False:
        commands.append(['foamToVTK', '-case', case, '-latestTime'])
    if (vr_pictures and os.path.exists(path_vr) == False) \
    or (vr_receptors and os.path.exists(path_vr_receptors) == False):
        angle = float(re.findall(r"\d+\.\d+", case)[0])
        commands.append(['pvpython', 'pv_vr.py', str(angle)])
    p = multiprocessing.Process(target=init_sbp, args=(commands, case, ),)
    p.start()


def init_sbp(commands, case):
    for cmd in commands:
        with open(os.path.join(case, '{0}.log'.format(cmd[0])), 'w') as f:
            subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT)