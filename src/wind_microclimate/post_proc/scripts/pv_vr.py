import os, sys, fnmatch
import logging
from paraview.simple import *
from pv_helpers import GroundPatch, Probe, VrColorbar 
from pv_helpers import read_pv_settings, read_receptors, create_vr


# manual settings
colorbar_disp = False
camera_scale = 200

#arguments passed while executing the script
case = sys.argv[1]
v_ref = sys.argv[2]
output_dir = sys.argv[3]
pv_input = sys.argv[4]
logfile = sys.argv[5]

# logging config
logging.basicConfig(filename=logfile, level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# read paraview input from file
settings = read_pv_settings(pv_input)

# assign inputs to local variables
vr_pictures = settings['vr_pictures']
vr_calculate = settings['vr_calculate']
vr_receptors = settings['vr_receptors']
camera_position = [int(settings['x_camera']), int(settings['y_camera']), 500]
z_ref = settings['h_ref']
receptors_file = settings['receptor_coords']
png_path = '%s/VR_%s.png' % (output_dir, os.path.split(case)[1])

vtk_dir = os.listdir('%s/VTK/' % (case))
pattern = '*.vtk'
vtks = []
# looks for VTK results
for name in vtk_dir:
    if fnmatch.fnmatch(name, pattern):
        vtks.append(name)
# finds most recent VTK file
vtk = sorted(vtks, reverse = True)[0]
vtk_path = '%s/VTK/%s' % (case, vtk)

if vr_pictures:
    ground_patches = settings['vr_surfaces'].split()
    logging.info('{0} - generating VR contours...'.format(os.path.split(case)[1]))
    patches = []
    # creates list with Patch objects in ParaView
    for name in ground_patches:
        patches.append(GroundPatch(name, case))

    # creates a translation of each patch at pedestrian height (z_ref)
    for p in patches:
        p.create_transform()
        p.transform.Transform = 'Transform'
        p.transform.Transform.Translate = [0.0, 0.0, z_ref]

    paraview.simple._DisableFirstRenderCameraReset()

    calculator1 = create_vr(vtk_path, v_ref)

    renderView1 = GetActiveViewOrCreate('RenderView')
    renderView1.ViewSize = [1625, 926]
    renderView1.Background = [1.0, 1.0, 1.0]

    # colorbar settings
    colorbar = VrColorbar('VR', renderView1)
    colorbar.set_defaults()
    colorbar.set_specifics()

    # creates VR contours on translated boundaries
    for p in patches:
        p.create_resample(calculator1)
        # exporting VR nodal values to CSV
        if vr_calculate:
            SaveData('%s/_VR_%s.csv' % (case, p.name), proxy=p.resample, 
                Precision=6)
        p.create_display(renderView1)
        p.display.ColorArrayName = ['POINTS', 'VR']
        p.display.LookupTable = colorbar.lut
        p.display.Ambient = 0.2
        p.display.SetScalarBarVisibility(renderView1, colorbar_disp)

    # camera settings
    renderView1.Update()
    renderView1.CameraPosition = camera_position
    renderView1.CameraParallelProjection = 1
    renderView1.CameraFocalPoint = [camera_position[0], camera_position[1], z_ref]
    renderView1.CameraParallelScale = camera_scale
    renderView1.OrientationAxesVisibility = 0

    # save image with the results
    SaveScreenshot(png_path, renderView1, ImageResolution=[2920, 1848])

if vr_receptors:
    logging.info('{0} - exporting VR data in receptor locations to CSV file...'
        .format(os.path.split(case)[1]))
    # reads file with receptor coordinates into a 2D list
    receptors = read_receptors(receptors_file)

    if not vr_pictures:
        calculator1 = create_vr(vtk_path, v_ref)

    probe_list = []
    # creates list with Probe objects in ParaView
    for i in range(len(receptors)):
        coords = [float(receptors[i][1]), float(receptors[i][2]), 
            float(receptors[i][3])]
        name = receptors[i][0]
        probe_list.append(Probe(calculator1, coords, name))

    spreadSheetView1 = CreateView('SpreadSheetView')
    spreadSheetView1.ColumnToSort = ''
    spreadSheetView1.BlockSize = 1024

    # exports VR data in all receptor (probe) locations to CSV files
    for p in probe_list:
        p.pv_obj.ProbeType.Center = p.coords
        p.create_sheet(spreadSheetView1)
        ExportView('%s/_VR_%s.csv' % (case, p.name), view=spreadSheetView1)
