import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
from System.utils import create_lattice_plane, create_ribbon, joint_list, create_ribbon_closed, create_lattice_sphere
import math

# TODO: Make eyelid group follow eye movement (with falloff)


def create_nasolabial(dict):
    grp_ctrl = cmds.group(em=True, n="nasolabial_control_group")
    cmds.matchTransform(grp_ctrl, "Facial")
    cmds.parent(grp_ctrl, "face_constrain_head")

    # Create projection lattice plane for both sides
    proj_surface = create_lattice_plane("Nasolabial", 40, 40, "proj_plane_nasolabial")
    cmds.parent(proj_surface[0], "face_constrain_head")

    # separate each side list
    jnts_all = cmds.listRelatives("Nasolabial")
    sides = ["_R", "_L"]
    for side in sides:
        jnt_sides = []
        for jnt in jnts_all:
            if side in jnt:
                jnt_sides.append(jnt)

        # # reorganize list index
        # upper_half = []
        # lower_half = []
        # for jnt in jnt_sides:
        #     if "upper" in jnt.lower():
        #         upper_half.append(jnt)
        #     elif "lower" in jnt.lower():
        #         lower_half.append(jnt)
        # upper_half.sort(reverse=True)
        # lower_half.sort()


        jnt_list = jnt_sides
        # jnt_list.append("EyelidOuterCorner{0}".format(side))
        # for jnt in upper_half:
        #     jnt_list.append(jnt)
        # jnt_list.append("EyelidInnerCourner{0}".format(side))
        # for jnt in lower_half:
        #     jnt_list.append(jnt)

        # jnt_list = joint_list("Eyelids", first_half="upper", second_half="lower",middle_joint="Eyelid_InnerCourner")
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
                ctrl = cmds.circle(n="ctrl_" + jnt, cy=1, r=0.75, nr=(0, 1, 0))
            elif "_l" in jnt.lower():
                ctrl = cmds.circle(n="ctrl_" + jnt, cy=-1, r=0.75, nr=(0, 1, 0))
            else:
                ctrl = cmds.circle(n="ctrl_" + jnt, cy=1, r=0.75, nr=(0, 1, 0))

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

        ribbon = create_ribbon("ribbon_Nasolabial{0}".format(side), jnt_list)
        param_u_step = ribbon[3]
        cmds.parent(ribbon[0], grp_ctrl)
        cmds.parent(ribbon[1], grp_ctrl)



        # Figure out the center most ctrl for upper and lower - It's temporary hardcoded, should find the midpoint between first half, and midpoint between second half
        # TODO: NEEDS 3 controls
        ctrl_upper_number = "2"
        ctrl_upper_name = "ctrl_Nasolabial" + ctrl_upper_number + "{0}".format(side)

        ctrl_lower_number = "4"
        ctrl_lower_name = "ctrl_Nasolabial" + ctrl_lower_number + "{0}".format(side)



        # Create the primary controls - Hardcoded based on ctrl above
        rib_point_list = ["NasolabialUpper{0}".format(side), "NasolabialLower{0}".format(side)]
        for rib_point in rib_point_list:
            grp_offset = cmds.group(em=True, n="offset_" + rib_point)
            grp_flip = cmds.group(em=True, n="flip_" + rib_point)
            grp_sdk = cmds.group(em=True, n="sdk_" + rib_point)
            if "_L" in rib_point:
                ctrl = cmds.circle(n="ctrl_" + rib_point, cy=-1, r=1, nr=(0, 1, 0))
            else:
                ctrl = cmds.circle(n="ctrl_" + rib_point, cy=1, r=1, nr=(0, 1, 0))
            mediator = cmds.group(em=True, n="mediator_" + rib_point)

            cmds.parent(ctrl[0], grp_sdk)
            cmds.parent(grp_sdk, grp_flip)
            cmds.parent(grp_flip, grp_offset)
            cmds.parent(grp_offset, grp_ctrl)
            cmds.xform(grp_offset, ro=(90, 0, 90))
            cmds.parent(mediator, "face_mediators")
            cmds.pointConstraint(ctrl, mediator)

            follicle = cmds.createNode("follicle")

            if "Upper" in rib_point:
                cmds.matchTransform(grp_offset, ctrl_upper_name, pos=True)
                follicle_transform = cmds.rename(cmds.listRelatives(follicle, p=True), "follicle_surface_NasolabialUpper{0}".format(side))
                cmds.select(d=True)
                rib_cjoint = cmds.joint(n="ribbon_cjoint_NasolabialUpper{0}".format(side))

            elif "Lower" in rib_point:
                cmds.matchTransform(grp_offset, ctrl_lower_name, pos=True)
                follicle_transform = cmds.rename(cmds.listRelatives(follicle, p=True), "follicle_surface_NasolabialLower{0}".format(side))
                cmds.select(d=True)
                rib_cjoint = cmds.joint(n="ribbon_cjoint_NasolabialLower{0}".format(side))

            cmds.setAttr(rib_cjoint + ".drawStyle", 2)
            cmds.parent(rib_cjoint, ctrl[0])
            cmds.xform(rib_cjoint, t=(0, 0, 0), ro=(0, 0, 0))
            cmds.makeIdentity(rib_cjoint, a=True, r=True)
            follicle = cmds.listRelatives(follicle_transform)[0]


            cmds.parent(follicle_transform, "face_system")



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


        cmds.matchTransform("offset_NasolabialUpper{0}".format(side), "Nasolabial" + ctrl_upper_number + "{0}".format(side))
        cmds.matchTransform("offset_NasolabialLower{0}".format(side), "Nasolabial" + ctrl_lower_number + "{0}".format(side))
        cmds.skinCluster("ribbon_cjoint_NasolabialUpper{0}".format(side), "ribbon_cjoint_NasolabialLower{0}".format(side), ribbon[0], tsb=True)

        # attach def joints to ctrl jnts
        for jnt in jnt_list:
            cmds.parent(cmds.pointConstraint("x_" + jnt, jnt), "face_constraints")
            cmds.parent(cmds.orientConstraint("x_" + jnt, jnt), "face_constraints")


def attach_nasolabial():
    # make sure brow ctrls are all zeroed out
    ctrl_list = cmds.listRelatives("Nasolabial")
    sides = ["_R", "_L"]
    for side in sides:
        ctrl_list.append("NasolabialUpper{0}".format(side))
        ctrl_list.append("NasolabialLower{0}".format(side))

    for ctrl in ctrl_list:
        cmds.xform("ctrl_" + ctrl, t=(0, 0, 0), ro=(0, 0, 0))

    const_grp = cmds.group(em=True, n="nasolabial_ribbon_constraint")
    cmds.parent(const_grp, "face_system")

    rib_jnts = ["NasolabialUpper_R", "NasolabialUpper_L", "NasolabialLower_R", "NasolabialLower_L"]
    for jnt in rib_jnts:
        cmds.parent("ribbon_cjoint_" + jnt, "follicle_surface_" + jnt)
        # cmds.xform(jnt, t=(0, 0, 0), ro=(90, 0, 90))
        cmds.xform("ribbon_cjoint_" + jnt, t=(0, 0, 0))
        # cmds.makeIdentity("ribbon_cjoint_" + jnt, a=True, r=True)
    cmds.select(d=True)

    jnt_list = cmds.listRelatives("Nasolabial")

    for jnt in jnt_list:
        const_pnt = cmds.pointConstraint("follicle_" + jnt, "sdk_" + jnt, mo=True)
        const_ori = cmds.orientConstraint("follicle_" + jnt, "sdk_" + jnt, mo=True)
        cmds.parent(const_pnt, const_grp)
        cmds.parent(const_ori, const_grp)
    cmds.select(d=True)


def detach_nasolabial():
    # make sure brow ctrls are all zeroed out
    ctrl_list = cmds.listRelatives("Nasolabial")
    sides = ["_R", "_L"]
    for side in sides:
        ctrl_list.append("NasolabialUpper{0}".format(side))
        ctrl_list.append("NasolabialLower{0}".format(side))

    for ctrl in ctrl_list:
        cmds.xform("ctrl_" + ctrl, t=(0, 0, 0), ro=(0, 0, 0))

    # make sure brow ctrls are all zeroed out
    cmds.delete("nasolabial_ribbon_constraint")
    cmds.select(d=True)

    rib_jnts = ["NasolabialUpper_R", "NasolabialUpper_L", "NasolabialLower_R", "NasolabialLower_L"]
    for jnt in rib_jnts:
        cmds.parent("ribbon_cjoint_" + jnt, "ctrl_" + jnt)
        cmds.xform("ribbon_cjoint_" + jnt, t=(0, 0, 0))
        # cmds.makeIdentity("ribbon_cjoint_" + jnt, a=True, r=True)
    cmds.select(d=True)


