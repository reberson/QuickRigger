import maya.cmds as cmds
from definitions import CONTROLS_DIR
from System.file_handle import file_read_yaml, import_curve

def create_jaw(dict):
    grp_ctrl = cmds.group(em=True, n="jaw_control_group")
    cmds.matchTransform(grp_ctrl, "Jaw_M")
    cmds.parent(grp_ctrl, "face_constrain_head")
    jnt_list = ["Jaw_M", "Chin_M", "Jaw_End_M"]

    # create base controls
    for jnt in jnt_list:
        jd = dict[jnt]
        grp_offset = cmds.group(em=True, n="offset_" + jnt)
        grp_flip = cmds.group(em=True, n="flip_" + jnt)
        grp_sdk = cmds.group(em=True, n="sdk_" + jnt)

        if "_r" in jnt.lower():
            ctrl = cmds.circle(n="ctrl_" + jnt, cy=1, r=0.25, nr=(0, 1, 0))
            cmds.setAttr(ctrl[0] + ".overrideEnabled", 1)
            cmds.setAttr(ctrl[0] + ".overrideColor", 13)
            ctrl = ctrl[0]
        elif "_l" in jnt.lower():
            ctrl = cmds.circle(n="ctrl_" + jnt, cy=-1, r=0.25, nr=(0, 1, 0))
            cmds.setAttr(ctrl[0] + ".overrideEnabled", 1)
            cmds.setAttr(ctrl[0] + ".overrideColor", 6)
            ctrl = ctrl[0]
        elif "jaw_m" in jnt.lower():
            # ctrl = cmds.circle(n="ctrl_" + jnt, cy=15, r=0.25, nr=(0, 1, 0))
            ctrl = cmds.rename(import_curve(file_read_yaml(CONTROLS_DIR + "cntrl_jaw.yaml")), "ctrl_" + jd[3])
            cmds.setAttr(ctrl + ".overrideEnabled", 1)
            cmds.setAttr(ctrl + ".overrideColor", 17)
        else:
            ctrl = cmds.circle(n="ctrl_" + jnt, cy=1, r=0.25, nr=(0, 1, 0))
            cmds.setAttr(ctrl[0] + ".overrideEnabled", 1)
            cmds.setAttr(ctrl[0] + ".overrideColor", 17)
            ctrl = ctrl[0]
        cmds.select(d=True)
        xjnt = cmds.joint(n="x_" + jnt)
        cmds.setAttr(xjnt + ".radius", 0.5)
        cmds.select(d=True)
        cmds.setAttr(xjnt + ".drawStyle", 2)
        if "_end" in jnt.lower():
            cmds.setAttr(ctrl + ".overrideVisibility", 0)
        cmds.parent(xjnt, ctrl)
        cmds.parent(ctrl, grp_flip)
        cmds.parent(grp_flip, grp_sdk)
        cmds.parent(grp_sdk, grp_offset)
        cmds.parent(grp_offset, grp_ctrl)
        cmds.xform(grp_offset, ws=True, t=jd[0], ro=jd[1], roo=jd[2])
        if "_L" in jnt:
            cmds.xform(grp_flip, r=True, ro=(0, 180, 0))

    #parent ctrls to jaw ctrl
    cmds.parent("offset_Chin_M", "x_Jaw_M")
    cmds.parent("offset_Jaw_End_M", "x_Jaw_M")

    # attach def joints to ctrl jnts
    for jnt in jnt_list:
        cmds.parent(cmds.pointConstraint("x_" + jnt, jnt), "face_constraints")
        cmds.parent(cmds.orientConstraint("x_" + jnt, jnt), "face_constraints")

    # make jaw locator follow jaw_end
    cmds.pointConstraint("x_Jaw_End_M", "loc_jaw")
    cmds.orientConstraint("x_Jaw_End_M", "loc_jaw")



