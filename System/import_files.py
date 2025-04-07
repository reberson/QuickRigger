import maya.cmds as cmds


def import_ctrl(file_path, ctrl_name):
    cmds.file(file_path, i=True)

    if cmds.objExists('control') == True:
        cmds.rename('control', ctrl_name)
    new_ctrl = ctrl_name
    return new_ctrl
