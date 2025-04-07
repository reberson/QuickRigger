import maya.cmds as cmds
from scripts.autorigger.shared.utils import create_lattice_plane, create_ribbon, joint_list
from scripts.autorigger.rig_tools.layout_tools import lattice_load


# TODO: create a toggle for follicle visibility
# TODO: change the code to be number agnostic of joints.
# TODO: Change the way the follicle controls attach to the far left, far right and center joints

def create_brow(dict):
    grp_ctrl = cmds.group(em=True, n="brow_control_group")
    cmds.matchTransform(grp_ctrl, "Facial")
    cmds.parent(grp_ctrl, "face_constrain_head")
    jnt_list = joint_list("Brows", "Brow_M", first_half="_r", second_half="_l")
    last_jnt = jnt_list[len(jnt_list) - 1]
    # declare existing projection groups
    grp_proj_rib = "face_ribbons"
    # create base controls
    for jnt in jnt_list:
        jd = dict[jnt]
        grp_offset = cmds.group(em=True, n="offset_" + jnt)
        grp_flip = cmds.group(em=True, n="flip_" + jnt)
        grp_sdk = cmds.group(em=True, n="sdk_" + jnt)
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
    ribbon = create_ribbon("ribbon_brow", jnt_list)
    cmds.parent(ribbon[0], grp_proj_rib)
    cmds.parent(ribbon[1], grp_proj_rib)

    # Create the primary controls
    rib_point_list = ["brow_outer_R", "brow_mid_R", "brow_inner_R", "brow_M", "brow_outer_L", "brow_mid_L", "brow_inner_L"]
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
        cmds.parent(ctrl[0], grp_sdk)
        cmds.parent(grp_sdk, grp_flip)
        cmds.parent(grp_flip, grp_offset)
        cmds.parent(grp_offset, grp_ctrl)
        cmds.xform(grp_offset, ro=(90, 0, 90))
        if rib_point == "brow_outer_R":
            cmds.matchTransform(grp_offset, "follicle_" + jnt_list[0], pos=True)
            cmds.select(d=True)
            rib_cjoint = cmds.joint(n="ribbon_cjoint_brow_outer_R")
        elif rib_point == "brow_inner_R":
            cmds.matchTransform(grp_offset, "follicle_Brow1_R", pos=True)
            cmds.select(d=True)
            rib_cjoint = cmds.joint(n="ribbon_cjoint_brow_inner_R")
        elif rib_point == "brow_M":
            cmds.matchTransform(grp_offset, "follicle_Brow_M", pos=True)
            cmds.select(d=True)
            rib_cjoint = cmds.joint(n="ribbon_cjoint_brow_M")
        elif rib_point == "brow_outer_L":
            cmds.matchTransform(grp_offset, "follicle_" + last_jnt, pos=True)
            cmds.select(d=True)
            rib_cjoint = cmds.joint(n="ribbon_cjoint_brow_outer_L")
            cmds.xform(grp_flip, r=True, ro=(0, 180, 0))
        elif rib_point == "brow_inner_L":
            cmds.matchTransform(grp_offset, "follicle_Brow1_L", pos=True)
            cmds.select(d=True)
            rib_cjoint = cmds.joint(n="ribbon_cjoint_brow_inner_L")
            cmds.xform(grp_flip, r=True, ro=(0, 180, 0))
        elif rib_point == "brow_mid_R":
            cmds.matchTransform(grp_offset, "follicle_Brow2_R", pos=True) # - temporary
            cmds.select(d=True)
            rib_cjoint = cmds.joint(n="ribbon_cjoint_brow_mid_R")
        elif rib_point == "brow_mid_L":
            cmds.matchTransform(grp_offset, "follicle_Brow2_L", pos=True) # - temporary
            cmds.select(d=True)
            rib_cjoint = cmds.joint(n="ribbon_cjoint_brow_mid_L")
            cmds.xform(grp_flip, r=True, ro=(0, 180, 0))
        cmds.setAttr(rib_cjoint + ".drawStyle", 2)
        cmds.parent(rib_cjoint, ctrl[0])
        cmds.xform(rib_cjoint, t=(0, 0, 0), ro=(0, 0, 0))
        cmds.makeIdentity(rib_cjoint, a=True, r=True)

    cmds.matchTransform("offset_brow_outer_R", jnt_list[0])
    cmds.matchTransform("offset_brow_inner_R", "Brow1_R")
    cmds.matchTransform("offset_brow_mid_R", "Brow2_R")  # - Temporary
    cmds.matchTransform("offset_brow_mid_L", "Brow2_L")  # - Temporary
    cmds.matchTransform("offset_brow_inner_L", "Brow1_L")
    cmds.matchTransform("offset_brow_M", "Brow_M")
    cmds.matchTransform("offset_brow_outer_L", last_jnt)
    cmds.skinCluster("ribbon_cjoint_brow_outer_R", "ribbon_cjoint_brow_M", "ribbon_cjoint_brow_outer_L", "ribbon_cjoint_brow_inner_R", "ribbon_cjoint_brow_inner_L", "ribbon_cjoint_brow_mid_R", "ribbon_cjoint_brow_mid_L", ribbon[0], tsb=True)

    # attach def joints to ctrl jnts
    for jnt in jnt_list:
        cmds.parent(cmds.pointConstraint("x_" + jnt, jnt), "face_constraints")
        cmds.parent(cmds.orientConstraint("x_" + jnt, jnt), "face_constraints")


def attach_brow():
    reset_controls()
    const_grp = cmds.group(em=True, n="brow_ribbon_constraint")
    cmds.parent(const_grp, "face_system")
    cmds.select(d=True)
    jnt_list = joint_list("Brows", "Brow_M", first_half="_r", second_half="_l")
    for jnt in jnt_list:
        # const_par = cmds.parentConstraint("follicle_" + jnt, "sdk_" + jnt, mo=True)
        const_par = cmds.parentConstraint("follicle_" + jnt, "sdk_" + jnt, mo=True, sr=["y"])
        cmds.setAttr(const_par[0] + ".interpType", 2)
        cmds.parent(const_par, const_grp)
    cmds.select(d=True)


def detach_brow():
    reset_controls()
    cmds.delete("brow_ribbon_constraint")
    cmds.select(d=True)


def create_lattice_brow():
    reset_controls()
    # declare projection system groups
    grp_proj_sys = "face_projection_system"
    grp_proj_fol = "face_projection_follicles"
    proj_plane = create_lattice_plane("Brows", 40, 40, "proj_plane_forehead")
    cmds.parent(proj_plane[0], grp_proj_sys)
    cmds.select(d=True)
    cmds.select(proj_plane[2][1])
    lattice_load("template_lattice_forehead.yaml")
    cmds.select(d=True)
    # Declare control list
    rib_point_list = ["brow_outer_R", "brow_mid_R", "brow_inner_R", "brow_M", "brow_outer_L", "brow_mid_L",
                      "brow_inner_L"]
    for rib_point in rib_point_list:
        # Declare existing ctrl
        ctrl = "ctrl_" + rib_point
        mediator = cmds.group(em=True, n="mediator_" + rib_point)
        cmds.parent(mediator, "face_mediators")
        cmds.pointConstraint(ctrl, mediator)
        follicle = cmds.createNode("follicle")
        follicle_transform = cmds.rename(cmds.listRelatives(follicle, p=True), "follicle_plane_" + rib_point)
        follicle = cmds.listRelatives(follicle_transform)[0]
        cmds.parent(follicle_transform, grp_proj_fol)
        cmds.connectAttr(proj_plane[3][0] + ".outMesh", follicle + ".inputMesh")
        cmds.connectAttr(proj_plane[3][0] + ".worldMatrix", follicle + ".inputWorldMatrix")
        cmds.connectAttr(follicle + ".outRotate", follicle_transform + ".rotate")
        cmds.connectAttr(follicle + ".outTranslate", follicle_transform + ".translate")
        cmds.setAttr(follicle + ".parameterV", 0.5)
        cmds.setAttr(follicle + ".parameterU", 0.5)
        close_pnt_node = cmds.createNode("closestPointOnMesh", n="closestPointOn" + rib_point)
        cmds.connectAttr(mediator + ".translate", close_pnt_node + ".inPosition")
        cmds.connectAttr(proj_plane[3][0] + ".worldMesh", close_pnt_node + ".inMesh")
        cmds.connectAttr(proj_plane[3][0] + ".worldMatrix", close_pnt_node + ".inputMatrix")
        cmds.connectAttr(close_pnt_node + ".result.parameterU", follicle + ".parameterU")
        cmds.connectAttr(close_pnt_node + ".result.parameterV", follicle + ".parameterV")


def attach_brow_lattice():
    reset_controls()
    # declare ctrls to be attached to lattice
    rib_jnts = ["brow_outer_R", "brow_M", "brow_outer_L", "brow_inner_R", "brow_inner_L", "brow_mid_R", "brow_mid_L"]
    const_proj_grp = cmds.group(em=True, n="brow_projection_constraint")
    cmds.parent(const_proj_grp, "face_system")
    for jnt in rib_jnts:
        const_par = cmds.parentConstraint("follicle_plane_" + jnt, "ribbon_cjoint_" + jnt, mo=True)
        cmds.setAttr(const_par[0] + ".interpType", 2)
        cmds.parent(const_par, const_proj_grp)
    cmds.select(d=True)


def detach_brow_lattice():
    reset_controls()
    # delete lattice constraints
    cmds.delete("brow_projection_constraint")
    cmds.select(d=True)
    # reset joints that were affect by lattice constraints
    rib_jnts = ["brow_outer_R", "brow_M", "brow_outer_L", "brow_inner_R", "brow_inner_L", "brow_mid_R", "brow_mid_L"]
    for jnt in rib_jnts:
        cmds.xform("ribbon_cjoint_" + jnt, t=(0, 0, 0), ro=(0, 0, 0))
    cmds.select(d=True)


def reset_controls():
    ctrl_list = joint_list("Brows", "Brow_M", first_half="_r", second_half="_l")
    ctrl_list.append("brow_outer_R")
    ctrl_list.append("brow_M")
    ctrl_list.append("brow_outer_L")
    ctrl_list.append("brow_inner_R")
    ctrl_list.append("brow_inner_L")
    for ctrl in ctrl_list:
        cmds.xform("ctrl_" + ctrl, t=(0, 0, 0), ro=(0, 0, 0))