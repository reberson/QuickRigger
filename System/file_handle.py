import maya.cmds as cmds
import yaml
import os
from pathlib import Path
import io


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


def import_ctrl(file_path, ctrl_name):
    cmds.file(file_path, i=True)

    if cmds.objExists('control') == True:
        cmds.rename('control', ctrl_name)
    new_ctrl = ctrl_name
    return new_ctrl


def export_curve():
    """Exports the curve object into yaml file"""
    curve_obj = cmds.ls(sl=True, v=True, tr=True)
    ctrl_curve = cmds.listRelatives(curve_obj, ad=True, shapes=True)
    curve_dict = {}
    for shape in ctrl_curve:
        nodes = cmds.listConnections(shape)
        cv_mode = "circle"
        if nodes is not None:
            for node in nodes:
                if "makeNurbCircle" in node:
                    cv_mode = "circle"
                else:
                    cv_mode = "curve"
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


def import_curve():
    curve_dict = file_dialog_yaml("Load curve", mode="r")
    created_curves = []
    for key in curve_dict:
        cv_list = []
        if curve_dict[key]['mode'] == 'circle':
            new_circle = cmds.circle(n="circle", r=25, normal=(0, 1, 0))
            cv_list.append(curve_dict[key]['points'])
            new_curve = new_circle[0]
            cmds.select(new_curve + '.cv[:]')
            cvs = cmds.ls(sl=True)[0]
            cvCount = int(cvs.split(':')[1].split(']')[0])
            for i in range(0, cvCount + 1):
                cv = new_curve + '.cv[{0}]'.format(i)
                cmds.xform(cv, t=curve_dict[key]['points'][i], ws=True)
            cmds.select(d=True)
            crv_uuid = cmds.ls(new_circle[0], uuid=True)
            new_curve_id = cmds.rename(new_circle[0], "circle" + crv_uuid[0].replace("-", "_"))
            created_curves.append(new_curve_id)
        elif curve_dict[key]['mode'] == 'curve':
            for i in curve_dict[key]['points']:
                cv_list.append(curve_dict[key]['points'][i])
            new_curve = cmds.curve(n="curve", p=cv_list)
            crv_uuid = cmds.ls(new_curve, uuid=True)
            new_curve_id = cmds.rename(new_curve, "circle" + crv_uuid[0].replace("-", "_"))
            cmds.select(new_curve_id + '.cv[:]')
            cmds.select(d=True)
            created_curves.append(new_curve_id)
    cmds.select(d=True)
    for item in created_curves:
        cmds.select(item, add=True)
    created_curves_new = cmds.ls(sl=True, v=True, tr=True, typ="nurbsCurve")
    shape_list = []
    for shape_node in created_curves_new:
        node = cmds.listRelatives(shape_node, s=True)
        shape_list.append(node)
    cmds.select(d=True)
    ctrl_grp = cmds.group(em=True, n="control")
    for curve_shape in shape_list:
        cmds.parent(curve_shape, ctrl_grp, r=True, s=True)
    for empty_curve in created_curves_new:
        cmds.delete(empty_curve)
    cmds.select(d=True)
