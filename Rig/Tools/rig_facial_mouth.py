import maya.cmds as cmds
from System.utils import create_lattice_plane, create_ribbon
from Rig.Tools.layout_tools import lattice_load

def create_mouth(dict):
    grp_ctrl = cmds.group(em=True, n="mouth_control_group")
    cmds.matchTransform(grp_ctrl, "Facial")
    cmds.parent(grp_ctrl, "face_constrain_head")

    # declare existing projection groups
    grp_proj_sys = "face_projection_system"
    grp_proj_fol = "face_projection_follicles"
    grp_proj_rib = "face_ribbons"

    proj_surface = create_lattice_plane("Mouth", 40, 40, "proj_plane_mouth")
    cmds.parent(proj_surface[0], grp_proj_sys)

    # Make lattice not inherit transforms so the plane won't have double transformation
    cmds.setAttr(proj_surface[2][0] + "Lattice" + ".inheritsTransform", 0)
    # Place lattice back to the original position
    cmds.matchTransform(proj_surface[2][0] + "Lattice", "Facial")

    cmds.select(d=True)
    cmds.select(proj_surface[2][1])
    lattice_load("template_lattice_mouth.yaml")
    cmds.select(d=True)
    cmds.skinCluster("Facial", "Jaw_End_M", proj_surface[3], tsb=True)
    cmds.select(d=True)


    jnt_list = cmds.listRelatives("Mouth")
    jnts_upper = []
    jnts_lower = []

    # create base controls
    for jnt in jnt_list:
        jd = dict[jnt]
        grp_offset = cmds.group(em=True, n="offset_" + jnt)
        grp_flip = cmds.group(em=True, n="flip_" + jnt)
        grp_sdk = cmds.group(em=True, n="sdk_" + jnt)
        # ctrl = cmds.circle(n="ctrl_" + jnt, cy=1, r=0.75, nr=(0, 1, 0))
        if "_r" in jnt.lower():
            ctrl = cmds.circle(n="ctrl_" + jnt, cy=1, r=0.25, nr=(0, 1, 0))
            cmds.setAttr(ctrl[0] + ".overrideEnabled", 1)
            cmds.setAttr(ctrl[0] + ".overrideColor", 31)
        elif "_l" in jnt.lower():
            ctrl = cmds.circle(n="ctrl_" + jnt, cy=-1, r=0.25, nr=(0, 1, 0))
            cmds.setAttr(ctrl[0] + ".overrideEnabled", 1)
            cmds.setAttr(ctrl[0] + ".overrideColor", 18)
        else:
            ctrl = cmds.circle(n="ctrl_" + jnt, cy=1, r=0.25, nr=(0, 1, 0))
            cmds.setAttr(ctrl[0] + ".overrideEnabled", 1)
            cmds.setAttr(ctrl[0] + ".overrideColor", 21)

        cmds.select(d=True)
        xjnt = cmds.joint(n="x_" + jnt)
        cmds.setAttr(xjnt + ".radius", 0.5)
        cmds.select(d=True)
        cmds.setAttr(xjnt + ".drawStyle", 2)
        cmds.parent(xjnt, ctrl[0])
        cmds.parent(ctrl[0], grp_flip)
        cmds.parent(grp_flip, grp_sdk)
        cmds.parent(grp_sdk, grp_offset)
        cmds.parent(grp_offset, grp_ctrl)
        cmds.xform(grp_offset, ws=True, t=jd[0], ro=jd[1], roo=jd[2])
        if "_L" in jnt:
            cmds.xform(grp_flip, r=True, ro=(0, 180, 0))

        if "upper" in jnt.lower():
            jnts_upper.append(jnt)
        elif "lower" in jnt.lower():
            jnts_lower.append(jnt)

    # -----------------Setting Upper lip joints in order for the ribbon------------
    jnts_upper_sorted = []
    jnts_upper_r = []
    jnts_upper_l = []
    for jnt in jnts_upper:
        if "_r" in jnt.lower():
            jnts_upper_r.append(jnt)
        elif "_l" in jnt.lower():
            jnts_upper_l.append(jnt)

    jnts_upper_r.sort(reverse=True)
    jnts_upper_l.sort()

    for jnt in jnt_list:
        if "corner_r" in jnt.lower():
            jnts_upper_sorted.append(jnt)
    for jnt in jnts_upper_r:
        jnts_upper_sorted.append(jnt)
    for jnt in jnts_upper:
        if "_m" in jnt.lower():
            jnts_upper_sorted.append(jnt)
    for jnt in jnts_upper_l:
        jnts_upper_sorted.append(jnt)
    for jnt in jnt_list:
        if "corner_l" in jnt.lower():
            jnts_upper_sorted.append(jnt)

    first_jnt_upper = jnts_upper_sorted[0]
    last_jnt_upper = jnts_upper_sorted[len(jnts_upper_sorted) - 1]
    mid_jnt_upper = jnts_upper_sorted[int(len(jnts_upper_sorted) / 2)]

    # -----------------Setting Lower lip joints in order for the ribbon------------
    jnts_lower_sorted = []
    jnts_lower_r = []
    jnts_lower_l = []
    for jnt in jnts_lower:
        if "_r" in jnt.lower():
            jnts_lower_r.append(jnt)
        elif "_l" in jnt.lower():
            jnts_lower_l.append(jnt)

    jnts_lower_r.sort(reverse=True)
    jnts_lower_l.sort()

    for jnt in jnt_list:
        if "corner_r" in jnt.lower():
            jnts_lower_sorted.append(jnt)
    for jnt in jnts_lower_r:
        jnts_lower_sorted.append(jnt)
    for jnt in jnts_lower:
        if "_m" in jnt.lower():
            jnts_lower_sorted.append(jnt)
    for jnt in jnts_lower_l:
        jnts_lower_sorted.append(jnt)
    for jnt in jnt_list:
        if "corner_l" in jnt.lower():
            jnts_lower_sorted.append(jnt)

    first_jnt_lower = jnts_lower_sorted[0]
    last_jnt_lower = jnts_lower_sorted[len(jnts_lower_sorted) - 1]
    mid_jnt_lower = jnts_lower_sorted[int(len(jnts_lower_sorted) / 2)]

    # ribbons setup section
    ribbon_upper = create_ribbon("ribbon_mouth_upper", jnts_upper_sorted)
    param_u_step_upper = ribbon_upper[3]
    cmds.parent(ribbon_upper[0], grp_proj_rib)
    cmds.parent(ribbon_upper[1], grp_proj_rib)

    ribbon_lower = create_ribbon("ribbon_mouth_lower", jnts_lower_sorted, duplicated="corner")
    param_u_step_lower = ribbon_lower[3]
    cmds.parent(ribbon_lower[0], grp_proj_rib)
    cmds.parent(ribbon_lower[1], grp_proj_rib)

    # Create the primary controls
    rib_point_list = ["mouthCorner_R", "mouthUpper_M", "mouthCorner_L", "mouthLower_M"]
    for rib_point in rib_point_list:
        grp_offset = cmds.group(em=True, n="offset_" + rib_point)
        grp_flip = cmds.group(em=True, n="flip_" + rib_point)
        grp_sdk = cmds.group(em=True, n="sdk_" + rib_point)
        if "_l" in rib_point.lower():
            ctrl = cmds.circle(n="ctrl_" + rib_point, cy=-1, r=1, nr=(0, 1, 0))
            cmds.setAttr(ctrl[0] + ".overrideEnabled", 1)
            cmds.setAttr(ctrl[0] + ".overrideColor", 6)
        elif "_r" in rib_point.lower():
            ctrl = cmds.circle(n="ctrl_" + rib_point, cy=1, r=1, nr=(0, 1, 0))
            cmds.setAttr(ctrl[0] + ".overrideEnabled", 1)
            cmds.setAttr(ctrl[0] + ".overrideColor", 13)
        else:
            ctrl = cmds.circle(n="ctrl_" + rib_point, cy=1, r=1, nr=(0, 1, 0))
            cmds.setAttr(ctrl[0] + ".overrideEnabled", 1)
            cmds.setAttr(ctrl[0] + ".overrideColor", 17)
        mediator = cmds.group(em=True, n="mediator_" + rib_point)

        cmds.parent(ctrl[0], grp_sdk)
        cmds.parent(grp_sdk, grp_flip)
        cmds.parent(grp_flip, grp_offset)
        cmds.parent(grp_offset, grp_ctrl)
        cmds.xform(grp_offset, ro=(90, 0, 90))
        cmds.parent(mediator, "face_mediators")
        cmds.pointConstraint(ctrl, mediator)
        # cmds.orientConstraint(ctrl, rib_cjoint)
        follicle = cmds.createNode("follicle")
        if rib_point == "mouthCorner_R":
            # cmds.matchTransform(grp_offset, "follicle_Brow_4_R", pos=True)
            cmds.matchTransform(grp_offset, "follicle_" + jnts_upper_sorted[0], pos=True)
            follicle_transform = cmds.rename(cmds.listRelatives(follicle, p=True), "follicle_plane_mouthCorner_R")
            cmds.select(d=True)
            rib_cjoint = cmds.joint(n="ribbon_cjoint_mouthCorner_R")
        elif rib_point == "mouthUpper_M":
            cmds.matchTransform(grp_offset, "follicle_" + mid_jnt_upper, pos=True)
            follicle_transform = cmds.rename(cmds.listRelatives(follicle, p=True), "follicle_plane_mouthUpper_M")
            cmds.select(d=True)
            rib_cjoint = cmds.joint(n="ribbon_cjoint_mouthUpper_M")
        elif rib_point == "mouthLower_M":
            cmds.matchTransform(grp_offset, "follicle_" + mid_jnt_lower, pos=True)
            follicle_transform = cmds.rename(cmds.listRelatives(follicle, p=True), "follicle_plane_mouthLower_M")
            cmds.select(d=True)
            rib_cjoint = cmds.joint(n="ribbon_cjoint_mouthLower_M")
        elif rib_point == "mouthCorner_L":
            cmds.matchTransform(grp_offset, "follicle_" + last_jnt_upper, pos=True)
            follicle_transform = cmds.rename(cmds.listRelatives(follicle, p=True), "follicle_plane_mouthCorner_L")
            cmds.select(d=True)
            rib_cjoint = cmds.joint(n="ribbon_cjoint_mouthCorner_L")
            cmds.xform(grp_flip, r=True, ro=(0, 180, 0))

        cmds.setAttr(rib_cjoint + ".drawStyle", 2)
        cmds.parent(rib_cjoint, ctrl[0])
        cmds.xform(rib_cjoint, t=(0, 0, 0), ro=(0, 0, 0))
        cmds.makeIdentity(rib_cjoint, a=True, r=True)
        follicle = cmds.listRelatives(follicle_transform)[0]

        # follicle = cmds.createNode("follicle", n="brow_follicle")
        # follicle_transform = cmds.listRelatives(follicle, p=True)
        cmds.parent(follicle_transform, grp_proj_fol)

        cmds.connectAttr(proj_surface[3][0] + ".outMesh", follicle + ".inputMesh")
        cmds.connectAttr(proj_surface[3][0] + ".worldMatrix", follicle + ".inputWorldMatrix")
        cmds.connectAttr(follicle + ".outRotate", follicle_transform + ".rotate")
        cmds.connectAttr(follicle + ".outTranslate", follicle_transform + ".translate")
        cmds.setAttr(follicle + ".parameterV", 0.5)
        cmds.setAttr(follicle + ".parameterU", 0.5)

        close_pnt_node = cmds.createNode("closestPointOnMesh", n="closestPointOn" + rib_cjoint)
        cmds.connectAttr(mediator + ".translate", close_pnt_node + ".inPosition")
        cmds.connectAttr(proj_surface[3][0] + ".worldMesh", close_pnt_node + ".inMesh")
        cmds.connectAttr(proj_surface[3][0] + ".worldMatrix", close_pnt_node + ".inputMatrix")
        cmds.connectAttr(close_pnt_node + ".result.parameterU", follicle + ".parameterU")
        cmds.connectAttr(close_pnt_node + ".result.parameterV", follicle + ".parameterV")

        # cmds.parent(rib_cjoint, follicle_transform)
        # cmds.xform(rib_cjoint, t=(0, 0, 0), ro=(90, 0, 90))
        # cmds.makeIdentity(rib_cjoint, a=True, r=True)

    cmds.matchTransform("offset_mouthCorner_R", jnts_upper_sorted[0])
    cmds.matchTransform("offset_mouthUpper_M", mid_jnt_upper)
    cmds.matchTransform("offset_mouthLower_M", mid_jnt_lower)
    cmds.matchTransform("offset_mouthCorner_L", last_jnt_upper)
    cmds.skinCluster("ribbon_cjoint_mouthCorner_R", "ribbon_cjoint_mouthUpper_M", "ribbon_cjoint_mouthCorner_L", ribbon_upper[0], tsb=True)
    cmds.skinCluster("ribbon_cjoint_mouthCorner_R", "ribbon_cjoint_mouthLower_M", "ribbon_cjoint_mouthCorner_L",
                     ribbon_lower[0], tsb=True)
    # attach def joints to ctrl jnts
    for jnt in jnt_list:
        cmds.parent(cmds.pointConstraint("x_" + jnt, jnt), "face_constraints")
        cmds.parent(cmds.orientConstraint("x_" + jnt, jnt), "face_constraints")

    # Constrain mouth corners to follow the jaw (with falloff)
    jnts_corner_ctrl = ["mouthCorner_R", "mouthCorner_L"]
    for jnt in jnts_corner_ctrl:
        grp_parent = cmds.group(em=True, n="group_" + jnt)
        cmds.matchTransform(grp_parent, "offset_" + jnt)
        cmds.parent(grp_parent, grp_ctrl)
        if "_l" in jnt.lower():
            cmds.xform(grp_parent, r=True, ro=(0, 180, 0))
        cmds.parent("offset_" + jnt, grp_parent)
        cmds.pointConstraint("Mouth", grp_parent, mo=True, w=0.7)
        cmds.pointConstraint("Jaw_End_M", grp_parent, mo=True, w=0.3)
        cmds.orientConstraint("Mouth", grp_parent, mo=True, w=0.7)
        cmds.orientConstraint("Jaw_M", grp_parent, mo=True, w=0.3)

    # Constrain mouth LowerLip to follow the jaw
    jnts_lower_ctrl = ["mouthLower_M"]
    for jnt in jnts_lower_ctrl:
        grp_parent = cmds.group(em=True, n="group_" + jnt)
        cmds.matchTransform(grp_parent, "offset_" + jnt)
        cmds.parent(grp_parent, grp_ctrl)
        cmds.parent("offset_" + jnt, grp_parent)
        cmds.pointConstraint("Mouth", grp_parent, mo=True, w=0.25)
        cmds.pointConstraint("Jaw_End_M", grp_parent, mo=True, w=0.75)
        cmds.orientConstraint("Mouth", grp_parent, mo=True, w=0.25)
        cmds.orientConstraint("Jaw_M", grp_parent, mo=True, w=0.75)

    # Constrain mouth UpperLip to follow the jaw
    jnts_upper_ctrl = ["mouthUpper_M"]
    for jnt in jnts_upper_ctrl:
        grp_parent = cmds.group(em=True, n="group_" + jnt)
        cmds.matchTransform(grp_parent, "offset_" + jnt)
        cmds.parent(grp_parent, grp_ctrl)
        cmds.parent("offset_" + jnt, grp_parent)
        cmds.pointConstraint("Mouth", grp_parent, mo=True, w=0.9)
        cmds.pointConstraint("Jaw_End_M", grp_parent, mo=True, w=0.1)
        cmds.orientConstraint("Mouth", grp_parent, mo=True, w=0.9)
        cmds.orientConstraint("Jaw_M", grp_parent, mo=True, w=0.1)


def attach_mouth():
    # make sure ctrls are all zeroed out
    ctrl_list = cmds.listRelatives("Mouth")
    ctrl_list.append("mouthCorner_R")
    ctrl_list.append("mouthUpper_M")
    ctrl_list.append("mouthLower_M")
    ctrl_list.append("mouthCorner_L")
    for ctrl in ctrl_list:
        cmds.xform("ctrl_" + ctrl, t=(0, 0, 0), ro=(0, 0, 0))
    const_grp = cmds.group(em=True, n="mouth_ribbon_constraint")
    cmds.parent(const_grp, "face_system")

    rib_jnts = ["mouthCorner_R", "mouthUpper_M", "mouthLower_M", "mouthCorner_L"]
    for jnt in rib_jnts:
        cmds.parent("ribbon_cjoint_" + jnt, "follicle_plane_" + jnt)
        cmds.xform("ribbon_cjoint_" + jnt, t=(0, 0, 0))
    cmds.select(d=True)

    jnt_list = cmds.listRelatives("Mouth")

    for jnt in jnt_list:
        # const_pnt = cmds.pointConstraint("follicle_" + jnt, "sdk_" + jnt, mo=True)
        # const_ori = cmds.orientConstraint("follicle_" + jnt, "sdk_" + jnt, mo=True)
        const_par = cmds.parentConstraint("follicle_" + jnt, "sdk_" + jnt, mo=True)
        cmds.setAttr(const_par[0] + ".interpType", 2)
        # cmds.parent(const_pnt, const_grp)
        # cmds.parent(const_ori, const_grp)
        cmds.parent(const_par, const_grp)
    cmds.select(d=True)


def detach_mouth():
    ctrl_list = cmds.listRelatives("Mouth")
    ctrl_list.append("mouthCorner_R")
    ctrl_list.append("mouthUpper_M")
    ctrl_list.append("mouthLower_M")
    ctrl_list.append("mouthCorner_L")
    for ctrl in ctrl_list:
        cmds.xform("ctrl_" + ctrl, t=(0, 0, 0), ro=(0, 0, 0))
    # make sure  ctrls are all zeroed out
    cmds.delete("mouth_ribbon_constraint")
    cmds.select(d=True)

    rib_jnts = ["mouthCorner_R", "mouthUpper_M", "mouthLower_M", "mouthCorner_L"]
    for jnt in rib_jnts:
        cmds.parent("ribbon_cjoint_" + jnt, "ctrl_" + jnt)
        cmds.xform("ribbon_cjoint_" + jnt, t=(0, 0, 0))
    cmds.select(d=True)


