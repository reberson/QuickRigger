import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
from System.utils import create_lattice_plane, create_ribbon, joint_list, create_ribbon_closed, create_lattice_sphere
from Rig.Tools.layout_tools import lattice_load
import math


def create_nasolabial(dict):
    grp_ctrl = cmds.group(em=True, n="nasolabial_control_group")
    cmds.matchTransform(grp_ctrl, "Facial")
    cmds.parent(grp_ctrl, "face_constrain_head")

    # declare existing projection groups
    grp_proj_sys = "face_projection_system"
    grp_proj_fol = "face_projection_follicles"
    grp_proj_rib = "face_ribbons"

    # Create projection lattice plane for both sides
    proj_surface = create_lattice_plane("Nasolabial", 40, 40, "proj_plane_nasolabial")
    cmds.parent(proj_surface[0], grp_proj_sys)
    # Make lattice not inherit transforms so the plane won't have double transformation
    cmds.setAttr(proj_surface[2][0] + "Lattice" + ".inheritsTransform", 0)
    # Place lattice back to the original position
    cmds.matchTransform(proj_surface[2][0] + "Lattice", "Facial")

    cmds.select(d=True)
    cmds.select(proj_surface[2][1])
    lattice_load("template_lattice_nasolabial.yaml")
    cmds.select(d=True)
    cmds.skinCluster("Facial", "Jaw_End_M", proj_surface[3], tsb=True)
    cmds.select(d=True)

    # separate each side list
    jnts_all = cmds.listRelatives("Nasolabial")
    sides = ["_R", "_L"]
    for side in sides:
        jnt_sides = []
        for jnt in jnts_all:
            if side in jnt:
                jnt_sides.append(jnt)

        jnt_list = jnt_sides
        first_jnt = jnt_list[0]
        last_jnt = jnt_list[len(jnt_list) - 1]

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
            if "_l" in jnt.lower():
                cmds.xform(grp_flip, r=True, ro=(0, 180, 0))

        if side == "_R":
            ribbon = create_ribbon("ribbon_Nasolabial{0}".format(side), jnt_list, direction=(1, 0, 0), reverse=False)
        else:
            ribbon = create_ribbon("ribbon_Nasolabial{0}".format(side), jnt_list, direction=(-1, 0, 0))

        param_u_step = ribbon[3]
        cmds.parent(ribbon[0], grp_proj_rib)
        cmds.parent(ribbon[1], grp_proj_rib)



        # Figure out the center most ctrl for upper and lower - It's temporary hardcoded, should find the midpoint between first half, and midpoint between second half
        ctrl_upper_number = "1"
        # ctrl_upper_name = "offset_Nasolabial" + ctrl_upper_number + "{0}".format(side)
        ctrl_upper_name = str(jnt_list[0])

        ctrl_lower_number = "4"
        # ctrl_lower_name = "offset_Nasolabial" + ctrl_lower_number + "{0}".format(side)
        ctrl_lower_name = str(jnt_list[len(jnt_list)-1])

        # Measures to get the position for mid control
        start = cmds.xform(ctrl_upper_name, q=True, ws=True, t=True)
        start_rot = cmds.xform(ctrl_upper_name, q=True, ws=True, ro=True)
        # start_roo = cmds.xform(ctrl_upper_name, q=True, ws=True, roo=True)
        end = cmds.xform(ctrl_lower_name, q=True, ws=True, t=True)
        start_v = OpenMaya.MVector(start[0], start[1], start[2])
        end_v = OpenMaya.MVector(end[0], end[1], end[2])
        mid_v = (end_v + start_v)/2

        # Create the primary controls - Hardcoded based on ctrl above
        rib_point_list = ["NasolabialUpper{0}".format(side), "NasolabialLower{0}".format(side), "NasolabialMid{0}".format(side)]
        for rib_point in rib_point_list:
            grp_offset = cmds.group(em=True, n="offset_" + rib_point)
            grp_flip = cmds.group(em=True, n="flip_" + rib_point)
            grp_sdk = cmds.group(em=True, n="sdk_" + rib_point)
            if "_l" in rib_point.lower():
                ctrl = cmds.circle(n="ctrl_" + rib_point, cy=-1, r=1, nr=(0, 1, 0))
                cmds.setAttr(ctrl[0] + ".overrideEnabled", 1)
                cmds.setAttr(ctrl[0] + ".overrideColor", 6)
            else:
                ctrl = cmds.circle(n="ctrl_" + rib_point, cy=1, r=1, nr=(0, 1, 0))
                cmds.setAttr(ctrl[0] + ".overrideEnabled", 1)
                cmds.setAttr(ctrl[0] + ".overrideColor", 13)
            mediator = cmds.group(em=True, n="mediator_" + rib_point)

            cmds.parent(ctrl[0], grp_sdk)
            cmds.parent(grp_sdk, grp_flip)
            cmds.parent(grp_flip, grp_offset)
            cmds.parent(grp_offset, grp_ctrl)
            cmds.xform(grp_offset, ro=(90, 0, 90))
            cmds.parent(mediator, "face_mediators")
            cmds.pointConstraint(ctrl, mediator)

            follicle = cmds.createNode("follicle")

            if "upper" in rib_point.lower():
                cmds.matchTransform(grp_offset, "offset_" + ctrl_upper_name, pos=True)
                follicle_transform = cmds.rename(cmds.listRelatives(follicle, p=True), "follicle_surface_NasolabialUpper{0}".format(side))
                cmds.select(d=True)
                rib_cjoint = cmds.joint(n="ribbon_cjoint_NasolabialUpper{0}".format(side))

            elif "lower" in rib_point.lower():
                cmds.matchTransform(grp_offset, "offset_" + ctrl_lower_name, pos=True)
                follicle_transform = cmds.rename(cmds.listRelatives(follicle, p=True), "follicle_surface_NasolabialLower{0}".format(side))
                cmds.select(d=True)
                rib_cjoint = cmds.joint(n="ribbon_cjoint_NasolabialLower{0}".format(side))

            elif "mid" in rib_point.lower():
                # cmds.matchTransform(grp_offset, "offset_" + ctrl_lower_name, pos=True)
                cmds.xform(grp_offset, ws=True, t=mid_v)
                if "_l" in rib_point.lower():
                    cmds.xform(grp_offset, r=True, ro=(0, 0, 180))
                follicle_transform = cmds.rename(cmds.listRelatives(follicle, p=True), "follicle_surface_NasolabialMid{0}".format(side))
                cmds.select(d=True)
                rib_cjoint = cmds.joint(n="ribbon_cjoint_NasolabialMid{0}".format(side))


            cmds.setAttr(rib_cjoint + ".drawStyle", 2)
            cmds.parent(rib_cjoint, ctrl[0])
            cmds.xform(rib_cjoint, t=(0, 0, 0), ro=(0, 0, 0))
            cmds.makeIdentity(rib_cjoint, a=True, r=True)
            follicle = cmds.listRelatives(follicle_transform)[0]

            if "_l" in rib_point.lower():
                cmds.xform(grp_flip, r=True, ro=(0, 180, 0))

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


        cmds.matchTransform("offset_NasolabialUpper{0}".format(side), "offset_Nasolabial" + ctrl_upper_number + "{0}".format(side))
        cmds.matchTransform("offset_NasolabialLower{0}".format(side), "offset_Nasolabial" + ctrl_lower_number + "{0}".format(side))
        cmds.xform("offset_NasolabialMid{0}".format(side), ws=True, t=mid_v)
        if "_r" in side.lower():
            cmds.xform("offset_NasolabialMid{0}".format(side), r=True, t=(-2.5, 0, 0), ro=(0, -20, 0))
        elif "_l" in side.lower():
            cmds.xform("offset_NasolabialMid{0}".format(side), r=True, t=(2.5, 0, 0), ro=(0, 20, 0))
            cmds.xform(grp_flip, r=True, ro=(180, 0, 0))
        cmds.skinCluster("ribbon_cjoint_NasolabialUpper{0}".format(side), "ribbon_cjoint_NasolabialLower{0}".format(side), "ribbon_cjoint_NasolabialMid{0}".format(side), ribbon[0], tsb=True)

        # attach def joints to ctrl jnts
        for jnt in jnt_list:
            cmds.parent(cmds.pointConstraint("x_" + jnt, jnt), "face_constraints")
            cmds.parent(cmds.orientConstraint("x_" + jnt, jnt), "face_constraints")

    # Constrain Last Nasolabial to follow the jaw (with falloff)
    jnts_lowerNaso_ctrl = ["NasolabialLower_R", "NasolabialLower_L"]
    for jnt in jnts_lowerNaso_ctrl:
        grp_parent = cmds.group(em=True, n="group_" + jnt)
        cmds.matchTransform(grp_parent, "offset_" + jnt)
        cmds.parent(grp_parent, grp_ctrl)
        if "_l" in jnt.lower():
            cmds.xform(grp_parent, r=True, ro=(0, 180, 0))
        cmds.parent("offset_" + jnt, grp_parent)
        cmds.pointConstraint("Nasolabial", grp_parent, mo=True, w=0.25)
        cmds.pointConstraint("Jaw_End_M", grp_parent, mo=True, w=0.75)
        cmds.orientConstraint("Nasolabial", grp_parent, mo=True, w=0.25)
        cmds.orientConstraint("Jaw_M", grp_parent, mo=True, w=0.75)


def attach_nasolabial():
    # make sure brow ctrls are all zeroed out
    ctrl_list = cmds.listRelatives("Nasolabial")
    sides = ["_R", "_L"]
    for side in sides:
        ctrl_list.append("NasolabialUpper{0}".format(side))
        ctrl_list.append("NasolabialLower{0}".format(side))
        ctrl_list.append("NasolabialMid{0}".format(side))

    for ctrl in ctrl_list:
        cmds.xform("ctrl_" + ctrl, t=(0, 0, 0), ro=(0, 0, 0))

    const_grp = cmds.group(em=True, n="nasolabial_ribbon_constraint")
    cmds.parent(const_grp, "face_system")

    rib_jnts = ["NasolabialUpper_R", "NasolabialUpper_L", "NasolabialLower_R", "NasolabialLower_L", "NasolabialMid_R", "NasolabialMid_L"]
    for jnt in rib_jnts:
        cmds.parent("ribbon_cjoint_" + jnt, "follicle_surface_" + jnt)
        cmds.xform("ribbon_cjoint_" + jnt, t=(0, 0, 0))
    cmds.select(d=True)

    jnt_list = cmds.listRelatives("Nasolabial")

    for jnt in jnt_list:
        # const_pnt = cmds.pointConstraint("follicle_" + jnt, "sdk_" + jnt, mo=True)
        # const_ori = cmds.orientConstraint("follicle_" + jnt, "sdk_" + jnt, mo=True)
        const_par = cmds.parentConstraint("follicle_" + jnt, "sdk_" + jnt, mo=True)
        cmds.setAttr(const_par[0] + ".interpType", 2)
        # cmds.parent(const_pnt, const_grp)
        # cmds.parent(const_ori, const_grp)
        cmds.parent(const_par, const_grp)
    cmds.select(d=True)


def detach_nasolabial():
    # make sure brow ctrls are all zeroed out
    ctrl_list = cmds.listRelatives("Nasolabial")
    sides = ["_R", "_L"]
    for side in sides:
        ctrl_list.append("NasolabialUpper{0}".format(side))
        ctrl_list.append("NasolabialLower{0}".format(side))
        ctrl_list.append("NasolabialMid{0}".format(side))

    for ctrl in ctrl_list:
        cmds.xform("ctrl_" + ctrl, t=(0, 0, 0), ro=(0, 0, 0))

    # make sure brow ctrls are all zeroed out
    cmds.delete("nasolabial_ribbon_constraint")
    cmds.select(d=True)

    rib_jnts = ["NasolabialUpper_R", "NasolabialUpper_L", "NasolabialLower_R", "NasolabialLower_L", "NasolabialMid_R", "NasolabialMid_L"]
    for jnt in rib_jnts:
        cmds.parent("ribbon_cjoint_" + jnt, "ctrl_" + jnt)
        cmds.xform("ribbon_cjoint_" + jnt, t=(0, 0, 0))
        # cmds.makeIdentity("ribbon_cjoint_" + jnt, a=True, r=True)
    cmds.select(d=True)


