import os, json
from paraview.simple import *

""" Helper classes and functions for pvpython scripts
    
    This module contains all utilities needed for execution of 
    pvpython (ParaView) scripts to post-process the CFD results. 
    
    Note: ParaView has a built-in python2 interpreter, without additional 
    packages installed, thus all code has to be compatible with pure python2. 
"""

class Patch(object):
    """ General class for surface objects in Paraview """

    def __init__(self, name, case_path):
        vtk_file = os.listdir('%s/VTK/%s' % (case_path, name))[0]
        self.name = name
        self.path = '%s/VTK/%s/%s' % (case_path, name, vtk_file)
        self.reader = LegacyVTKReader(FileNames=self.path)


class GroundPatch(Patch):
    """ Subclass for ground surfaces above which results are displayed """

    def create_transform(self):
        self.transform = Transform(Input=self.reader)

    def create_resample(self, calculator):
        self.resample = ResampleWithDataset(Input=calculator, 
            Source=self.transform)

    def create_display(self, render_view):
        self.display = Show(self.resample, render_view)


class BuildingPatch(Patch):
    """ Subclass for building/structure surfaces to be displayed together 
        with the results """

    def __init__(self, name, case_path, of_interest):
        super(BuildingPatch, self).__init__(name, case_path)
        self.of_interest = of_interest
        self.edges = FeatureEdges(Input=self.reader)

    def create_display(self, render_view):
        self.display1 = Show(self.reader, render_view)
        self.display2 = Show(self.edges, render_view)


class Point(object):
    """ Class for the display of point objects in ParaView """

    def __init__(self, coords, name):
        self.coords = coords
        self.name = name
        self.pv_obj = PointSource()

    def create_display(self, render_view):
        self.display = Show(self.pv_obj, render_view)
    
    def delete(self):
        Delete(self.pv_obj)
        del self.pv_obj


class Text(object):
    """ Class for the display of text objects in ParaView """

    def __init__(self, origin, txt):
        self.pv_obj = a3DText()
        self.origin = origin
        self.txt = txt

    def create_display(self, render_view): 
        self.display = Show(self.pv_obj, render_view)

    def delete(self):
        Delete(self.pv_obj)
        del self.pv_obj


class Probe():
    """ Class for the Probe objects in ParaView """

    def __init__(self, source, coords, name):
        self.pv_obj = ProbeLocation(Input=source, 
            ProbeType='Fixed Radius Point Source')
        self.name = name
        self.coords = coords

    def create_sheet(self, sheet_view):
        self.sheet = Show(self.pv_obj, sheet_view)


class Colorbar(object):
    """ General class for colorbar objects in ParaView """

    def __init__(self, field, render_view):
        self.lut = GetColorTransferFunction(field)
        self.pwf = GetOpacityTransferFunction(field)
        self.colorbar = GetScalarBar(self.lut, render_view)
        
    def set_defaults(self):
        self.colorbar.WindowLocation = 'UpperLeftCorner'
        self.colorbar.LabelColor = [1.0, 1.0, 1.0]
        self.colorbar.LabelFontSize = 17
        self.colorbar.LabelBold = 1
        self.colorbar.Title = ''
        self.colorbar.ComponentTitle = ''
        self.colorbar.TitleBold = 1
        self.colorbar.DrawTickMarks = 0
        self.colorbar.AddRangeLabels = 0
        self.colorbar.DrawTickLabels = 1
        self.colorbar.ScalarBarThickness = 30
        self.colorbar.ScalarBarLength = 0.3


class VrColorbar(Colorbar):
    """ Colorbar objects for VR results in ParaView """

    def set_specifics(self):
        self.lut.ApplyPreset('Blue to Red Rainbow', True)
        self.lut.RescaleTransferFunction(0.0, 1.0)
        self.pwf.RescaleTransferFunction(0.0, 1.0)
        self.lut.NumberOfTableValues = 20
        self.colorbar.Title = 'VR'
        self.colorbar.TitleFontFamily = 'Times'
        self.colorbar.LabelFontFamily = 'Times'
        self.colorbar.TitleColor = [0.0, 0.0, 0.0]
        self.colorbar.LabelColor = [0.0, 0.0, 0.0]
        self.colorbar.TitleBold = 0
        self.colorbar.DrawTickMarks = 1
        self.colorbar.AutomaticLabelFormat = 0
        self.colorbar.UseCustomLabels = 1
        self.colorbar.CustomLabels = \
            [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        self.colorbar.LabelFormat = '%-#0.1f'


class LawsonColorbar(Colorbar):
    """ Colorbar objects for wind comfort map results in ParaView """

    def __init__(self, field, render_view):
        super(LawsonColorbar, self).__init__(field, render_view)
        self.annotations = ['0', 'A Frequent sitting ', 
            '1', 'B Occasional sitting ',
            '2', 'C Standing',
            '3', 'D Walking',
            '4', 'Uncomfortable']
    def set_specifics(self):
        self.lut.ApplyPreset('jet', True)
        self.lut.RescaleTransferFunction(0.0, 4.0)
        self.pwf.RescaleTransferFunction(0.0, 4.0)
        self.lut.Annotations = self.annotations
        self.lut.NumberOfTableValues = 5
        self.colorbar.DrawTickLabels = 0


def create_vr(vtk_path, v_ref):
    """Create custom Velocity Ratio scalar in ParaView"""

    case_vtk = LegacyVTKReader(FileNames=[vtk_path])
    calculator = Calculator(Input=case_vtk)
    calculator.Function = 'sqrt(U_X^2+U_Y^2+U_Z^2)/%s' % (v_ref)
    calculator.ResultArrayName = 'VR'
    return calculator


# reads paraview settings (camera, patch names etc.) from file
def read_pv_settings(txt_path):
    with open(txt_path) as settings:
        return json.load(settings)


# reads txt file with receptor locations into a 2D list
def read_receptors(csv_path):
    line_list = []
    with open(csv_path) as receptors:
        line_list = receptors.readlines()
    list_2d = []
    for c in range(len(line_list)):
        list_2d.append(line_list[c].split(','))
    return list_2d
