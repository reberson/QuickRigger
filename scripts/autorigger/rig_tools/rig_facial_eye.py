import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
from scripts.autorigger.shared.utils import connect_parent_constraint


def create_eye(dict):
    grp_ctrl = cmds.group(em=True, n="eye_control_group")
    cmds.matchTransform(grp_ctrl, "Facial")
    cmds.parent(grp_ctrl, "face_constrain_head")
    # check all eyes (can be just one, or even more than 2)
    jnt_list_all = cmds.listRelatives("Facial", ad=True)
    jnt_list = []
    jnt_list_ends = []
    for jnt in jnt_list_all:
        if "eye_" in jnt.lower():
            jnt_list.append(jnt)
    jnt_list.sort()

    # create fk controls
    for jnt in jnt_list:
        jd = dict[jnt]
        grp_offset = cmds.group(em=True, n="fk_offset_" + jnt)
        grp_flip = cmds.group(em=True, n="fk_flip_" + jnt)
        grp_sdk = cmds.group(em=True, n="fk_sdk_" + jnt)
        loc_up = cmds.spaceLocator(n="loc_" + jnt)
        if "_r" in jnt.lower():
            ctrl = cmds.circle(n="fk_" + jnt, cy=5, r=1.5, nr=(0, 1, 0))
            cmds.setAttr(ctrl[0] + ".overrideEnabled", 1)
            cmds.setAttr(ctrl[0] + ".overrideColor", 13)
        elif "_l" in jnt.lower():
            ctrl = cmds.circle(n="fk_" + jnt, cy=-5, r=1.5, nr=(0, 1, 0))
            cmds.setAttr(ctrl[0] + ".overrideEnabled", 1)
            cmds.setAttr(ctrl[0] + ".overrideColor", 6)
        else:
            ctrl = cmds.circle(n="fk_" + jnt, cy=5, r=1.5, nr=(0, 1, 0))
            cmds.setAttr(ctrl[0] + ".overrideEnabled", 1)
            cmds.setAttr(ctrl[0] + ".overrideColor", 17)
        cmds.select(d=True)
        xjnt = cmds.joint(n="fkx_" + jnt)
        cmds.setAttr(xjnt + ".radius", 0.5)
        cmds.select(d=True)
        cmds.setAttr(xjnt + ".drawStyle", 2)
        if "_end" in jnt.lower():
            # cmds.setAttr(ctrl[0] + ".overrideVisibility", 0)
            jnt_list_ends.append(jnt)
        cmds.parent(xjnt, ctrl[0])
        cmds.parent(ctrl[0], grp_flip)
        cmds.parent(grp_flip, grp_sdk)
        cmds.parent(grp_sdk, grp_offset)
        cmds.parent(grp_offset, grp_ctrl)
        # create space locator to be the Up aim vector
        cmds.parent(loc_up[0], grp_ctrl)
        cmds.xform(loc_up[0], ws=True, t=jd[0], ro=jd[1], roo=jd[2])
        cmds.xform(loc_up[0], r=True, t=(0, 10, 0))
        cmds.setAttr(cmds.listRelatives(loc_up[0])[0] + ".overrideEnabled", 1)
        cmds.setAttr(cmds.listRelatives(loc_up[0])[0] + ".overrideVisibility", 0)
        cmds.xform(grp_offset, ws=True, t=jd[0], ro=jd[1], roo=jd[2])
        if "_l" in jnt.lower():
            cmds.xform(grp_flip, r=True, ro=(0, 180, 0))
        # constrain def joints to ctrl joints
        cmds.parent(cmds.pointConstraint("fkx_" + jnt, jnt), "face_constraints")
        cmds.parent(cmds.orientConstraint("fkx_" + jnt, jnt), "face_constraints")

    # Parent end joints to their respective eye jnts
    for jnt in jnt_list_ends:
        jnt_parent = jnt.split("_End")[0] + jnt.split("_End")[1]
        cmds.parent("fk_offset_" + jnt, "fkx_" + jnt_parent)

    # Create AIM Main Eye control
    aim_follow_grp = cmds.group(em=True, n="group_follow_EyeAim")
    aim_grp = cmds.group(em=True, n="offset_EyeAim")
    aim_flip = cmds.group(em=True, n="flip_EyeAim")
    aim_sdk = cmds.group(em=True, n="sdk_EyeAim")
    aim_ctrl = cmds.circle(n="ctrl_EyeAim", r=2, nr=(0, 1, 0))
    cmds.setAttr(aim_ctrl[0] + ".overrideEnabled", 1)
    cmds.setAttr(aim_ctrl[0] + ".overrideColor", 17)
    cmds.parent(aim_ctrl[0], aim_flip)
    cmds.parent(aim_flip, aim_sdk)
    cmds.parent(aim_sdk, aim_grp)
    cmds.parent(aim_grp, aim_follow_grp)
    cmds.parent(aim_follow_grp, grp_ctrl)

    # reorient to face Y forward and z Up (just to keep standard)
    cmds.xform(aim_follow_grp, r=True, ro=(90, 0, 180))

    # Define the correct spot for the Aim origin
    # first check if there's more than one eye
    if cmds.objExists(jnt_list[1]):
        # get measure from first to last jnt in list
        start = cmds.xform(jnt_list[0], q=True, ws=True, t=True)
        end = cmds.xform(jnt_list[len(jnt_list)-1], q=True, ws=True, t=True)
        start_v = OpenMaya.MVector(start[0], start[1], start[2])
        end_v = OpenMaya.MVector(end[0], end[1], end[2])
        origin_v = (end_v + start_v) / 2
    else:
        # get the eye position and offset forward
        origin = cmds.xform(jnt_list[0], q=True, ws=True, t=True)
        origin_v = OpenMaya.MVector(origin[0], origin[1], origin[2])
    cmds.xform(aim_follow_grp, ws=True, t=origin_v)

    # create AIM individual controls
    for jnt in jnt_list:
        jd = dict[jnt]
        if "_end" not in jnt.lower():
            grp_offset = cmds.group(em=True, n="aim_offset_" + jnt)
            grp_flip = cmds.group(em=True, n="aim_flip_" + jnt)
            grp_sdk = cmds.group(em=True, n="aim_sdk_" + jnt)
            if "_r" in jnt.lower():
                ctrl = cmds.circle(n="aim_" + jnt, r=0.5, nr=(0, 1, 0))
                cmds.setAttr(ctrl[0] + ".overrideEnabled", 1)
                cmds.setAttr(ctrl[0] + ".overrideColor", 13)
            elif "_l" in jnt.lower():
                ctrl = cmds.circle(n="aim_" + jnt, r=0.5, nr=(0, 1, 0))
                cmds.setAttr(ctrl[0] + ".overrideEnabled", 1)
                cmds.setAttr(ctrl[0] + ".overrideColor", 6)
            else:
                ctrl = cmds.circle(n="aim_" + jnt, r=0.5, nr=(0, 1, 0))
                cmds.setAttr(ctrl[0] + ".overrideEnabled", 1)
                cmds.setAttr(ctrl[0] + ".overrideColor", 17)
            cmds.select(d=True)
            xjnt = cmds.joint(n="aimx_" + jnt)
            cmds.setAttr(xjnt + ".radius", 0.5)
            cmds.select(d=True)
            cmds.setAttr(xjnt + ".drawStyle", 2)
            cmds.parent(xjnt, ctrl[0])
            cmds.parent(ctrl[0], grp_flip)
            cmds.parent(grp_flip, grp_sdk)
            cmds.parent(grp_sdk, grp_offset)
            cmds.xform(grp_offset, ws=True, t=jd[0], ro=jd[1], roo=jd[2])
            cmds.parent(grp_offset, aim_ctrl[0])
            if "_l" in jnt.lower():
                cmds.xform(grp_flip, r=True, ro=(0, 180, 0))

    # after each eye ctrl is created and parented to the main Aim, offset the whole aim forward
    cmds.xform(aim_follow_grp, r=True, t=(0, 0, 30))

    # create AIM constraint for each eye
    for jnt in jnt_list:
        if "_end" not in jnt.lower():
            cmds.aimConstraint("aimx_" + jnt, "fk_sdk_" + jnt, aim=(0, 1, 0), u=(0, 0, 1), mo=True, wut="object", wuo="loc_" + jnt)

    # create parent constraint for aim group to swap between following head to main
    # Create global attribute on aim ctrl
    cmds.addAttr("ctrl_EyeAim", longName="global", attributeType="double", min=0, max=1, dv=0)
    cmds.setAttr("ctrl_EyeAim.global", e=True, channelBox=True)
    cmds.setAttr("ctrl_EyeAim.global", 1)
    # constrain to both face and origin
    connect_parent_constraint(aim_follow_grp, "face_constrain_head", "face_origin", "ctrl_EyeAim.global")