import maya.cmds as cmds
import yaml
import os
from pathlib import Path
import io


def import_ctrl(file_path, ctrl_name):
    cmds.file(file_path, i=True)

    if cmds.objExists('control') == True:
        cmds.rename('control', ctrl_name)
    new_ctrl = ctrl_name
    return new_ctrl


def export_curve():
    """Exports the curve object into yaml file"""
    curve_obj = cmds.ls(v=True, tr=True)
    ctrl_curve = cmds.listRelatives(curve_obj, ad=True, shapes=True)
    curve_dict = {}
    # TODO: change the curve/circle detection to not require specific naming
    # TODO: create checkers to make sure it's only one object in scene, or change to selected object.
    for shape in ctrl_curve:
        if "circle" in shape:
            cv_mode = "circle"
        else:
            cv_mode = "curve"
        cv_points = {}
        shape_dict = {'mode': cv_mode, 'points': cv_points}
        curve_dict[shape] = shape_dict

    for shape_dict in curve_dict:
        cmds.select(shape_dict + '.cv[:]')
        cvs = cmds.ls(sl=True)[0]
        cvCount = int(cvs.split(':')[1].split(']')[0])  # gets number of points in curve
        for i in range(0, cvCount + 1):
            cv = shape_dict + '.cv[{0}]'.format(i)
            position = [round(value, 5) for value in cmds.xform(cv, q=True, t=True, ws=True)]
            curve_dict[shape_dict]['points'][i] = position
    cmds.select(d=True)
    file_dialog_yaml("Save curve into yaml", mode="w", saved_data=curve_dict)


def file_dialog_yaml(title, mode, saved_data=None):
    """Creates file dialog to load or save Yaml files"""
    if saved_data is None:
        saved_data = {}
    if mode == "w":
        dialog = cmds.fileDialog2(bbo=1, cap=title, ds=2, ff="*.yaml;;*.yml", fm=0)
        output = Path(dialog[0])
        with io.open(output, "w") as stream:
            yaml.dump(saved_data, stream, default_flow_style=False, allow_unicode=True)
    elif mode == "r":
        dialog = cmds.fileDialog2(bbo=1, cap=title, ds=2, ff="*.yaml;;*.yml", fm=1)
        output = Path(dialog[0])
        with open(output, "r") as stream:
            loaded_data = yaml.load(stream, Loader=yaml.FullLoader)
        return loaded_data
