import sys, os, logging
from paraview.simple import *
from pv_helpers import BuildingPatch, LawsonColorbar, read_pv_settings


# manual settings
colorbar_disp = False
camera_scale = 200

case = sys.argv[1]
lawson_csv = sys.argv[2]
pv_input = sys.argv[3]
logfile = sys.argv[4]

# logging config
logging.basicConfig(filename=logfile, level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# read paraview input from file
settings = read_pv_settings(pv_input)

# assign inputs to local variables
bld_of_interest = settings['bld_of_interest'].split()
other_bld = settings['other_bld'].split()
camera_position = [int(settings['x_camera']), int(settings['y_camera']), 500]
z_ref = settings['h_ref']

# image file
lawson_png = lawson_csv.replace('.csv', '.png')

paraview.simple._DisableFirstRenderCameraReset()
renderView1 = FindViewOrCreate('RenderView1', viewtype='RenderView')
renderView1.ViewSize = [1625, 926]
SetActiveView(renderView1)
# camera settings
renderView1.CameraPosition = camera_position
renderView1.CameraParallelProjection = 1
renderView1.CameraFocalPoint = [camera_position[0], camera_position[1], z_ref]
renderView1.CameraParallelScale = camera_scale
renderView1.OrientationAxesVisibility = 0

# creating Patch objects in Paraview
patches = []
for name in bld_of_interest:
    patches.append(BuildingPatch(name, '%s_0.0' % (case), True))
for name in other_bld:
    patches.append(BuildingPatch(name, '%s_0.0' % (case), False))

# displays buildings and colours them appropriately
for p in patches:
    p.edges.FeatureAngle = 60.0
    p.create_display(renderView1)
    if p.of_interest == True:
        p.display1.SpecularColor = [1.0, 1.0, 1.0]
        p.display1.SetRepresentationType('Surface')
        p.display1.DiffuseColor = [0.85, 0.81, 0.58]
        p.display1.Specular = 100
        p.display1.Ambient = 0.1
        p.display1.Diffuse = 1.0
        p.display1.Opacity = 1.0
    else:
        p.display1.SpecularColor = [1.0, 1.0, 1.0]
        p.display1.SetRepresentationType('Surface')
        p.display1.DiffuseColor = [0.58, 0.58, 0.58]
        p.display1.Specular = 50
        p.display1.Ambient = 0.0
        p.display1.Diffuse = 1.0
    p.display2.DiffuseColor = [0.0, 0.0, 0.0]
    p.display2.LineWidth = 1.0

if not os.path.exists(lawson_csv):
    print(lawson_csv)
    sys.exit(logging.error('Could not find a CSV file with Lawson class data'))

logging.info('Generating colour map of wind comfort categories...')
# reads CSV file with nodal wind class data
reader = CSVReader(FileName=['%s' % (lawson_csv)])
tableToPoints1 = TableToPoints(Input=reader)
tableToPoints1.XColumn = 'Points:0'
tableToPoints1.YColumn = 'Points:1'
tableToPoints1.ZColumn = 'Points:2'

# colorbar settings
colorbar = LawsonColorbar('Class', renderView1)
colorbar.set_defaults()
colorbar.set_specifics()

# creates a wind class colour map by interpolating nodal data
delaunay2D1 = Delaunay2D(Input=tableToPoints1)
delaunay2D1Display = Show(delaunay2D1, renderView1)
delaunay2D1Display.ColorArrayName = ['POINTS', 'Class']
delaunay2D1Display.LookupTable = colorbar.lut
delaunay2D1Display.OSPRayScaleArray = 'Class'
delaunay2D1Display.SetScalarBarVisibility(renderView1, colorbar_disp)

SaveScreenshot(lawson_png, renderView1, ImageResolution=[2920, 1848])

# hides colour map
Hide(delaunay2D1, renderView1)
