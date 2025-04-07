import maya.cmds as cmds
from System.utils import create_ribbon_closed, create_lattice_sphere
import math

# TODO: Make eyelid group follow eye movement (with falloff)
# TODO : Fix Eye corner (inner and outer) ctrl orientations


def create_eyelid(dict):
    grp_ctrl = cmds.group(em=True, n="eyelid_control_group")
    cmds.matchTransform(grp_ctrl, "Facial")
    cmds.parent(grp_ctrl, "face_constrain_head")

    # declare existing projection groups
    grp_proj_sys = "face_projection_system"
    grp_proj_fol = "face_projection_follicles"
    grp_proj_rib = "face_ribbons"

    # separate each side list
    jnts_all = cmds.listRelatives("Eyelids")
    sides = ["_R", "_L"]
    for side in sides:
        jnt_sides = []
        for jnt in jnts_all:
            if side in jnt:
                jnt_sides.append(jnt)

        # reorganize list index
        upper_half = []
        lower_half = []
        for jnt in jnt_sides:
            if "upper" in jnt.lower():
                upper_half.append(jnt)
            elif "lower" in jnt.lower():
                lower_half.append(jnt)
        upper_half.sort(reverse=True)
        lower_half.sort()

        jnt_list = []
        jnt_list.append("EyelidOuterCorner{0}".format(side))
        for jnt in upper_half:
            jnt_list.append(jnt)
        jnt_list.append("EyelidInnerCorner{0}".format(side))
        for jnt in lower_half:
            jnt_list.append(jnt)

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
                cmds.setAttr(ctrl[0] + ".overrideEnabled", 1)
                cmds.setAttr(ctrl[0] + ".overrideColor", 31)
            elif "_l" in jnt.lower():
                ctrl = cmds.circle(n="ctrl_" + jnt, cy=-1, r=0.75, nr=(0, 1, 0))
                cmds.setAttr(ctrl[0] + ".overrideEnabled", 1)
                cmds.setAttr(ctrl[0] + ".overrideColor", 18)
            else:
                ctrl = cmds.circle(n="ctrl_" + jnt, cy=1, r=0.75, nr=(0, 1, 0))
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

        if side =="_R":
            ribbon = create_ribbon_closed("ribbon_eyelid{0}".format(side), jnt_list, "Eye{0}".format(side), left_side=False)
        else:
            ribbon = create_ribbon_closed("ribbon_eyelid{0}".format(side), jnt_list, "Eye{0}".format(side), left_side=True)
        param_u_step = ribbon[3]
        cmds.parent(ribbon[0], grp_proj_rib)
        cmds.parent(ribbon[1], grp_proj_rib)

        proj_sphere = create_lattice_sphere("Eye{0}".format(side), 3, "proj_sphere_eye{0}".format(side))
        cmds.parent(proj_sphere[0], grp_proj_sys)

        # Figure out the center most ctrl for upper and lower

        ctrl_upper_number = str(math.ceil((len(upper_half)/2)))
        ctrl_upper_name = "ctrl_EyelidUpper" + ctrl_upper_number + "{0}".format(side)

        ctrl_lower_number = str(math.ceil((len(upper_half)/2)))
        ctrl_lower_name = "ctrl_EyelidLower" + ctrl_lower_number + "{0}".format(side)



        # Create the primary controls
        rib_point_list = ["eyelidUpper{0}".format(side), "eyelidLower{0}".format(side), "eyelidInnerCorner{0}".format(side), "eyelidOuterCorner{0}".format(side)]
        for rib_point in rib_point_list:
            grp_offset = cmds.group(em=True, n="offset_" + rib_point)
            grp_flip = cmds.group(em=True, n="flip_" + rib_point)
            grp_sdk = cmds.group(em=True, n="sdk_" + rib_point)
            if "_L" in rib_point:
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

            if "Upper" in rib_point:
                cmds.matchTransform(grp_offset, ctrl_upper_name, pos=True)
                follicle_transform = cmds.rename(cmds.listRelatives(follicle, p=True), "follicle_sphere_eyelidUpper{0}".format(side))
                cmds.select(d=True)
                rib_cjoint = cmds.joint(n="ribbon_cjoint_eyelidUpper{0}".format(side))

            elif "Lower" in rib_point:
                cmds.matchTransform(grp_offset, ctrl_lower_name, pos=True)
                follicle_transform = cmds.rename(cmds.listRelatives(follicle, p=True), "follicle_sphere_eyelidLower{0}".format(side))
                cmds.select(d=True)
                rib_cjoint = cmds.joint(n="ribbon_cjoint_eyelidLower{0}".format(side))

            elif "innercorner" in rib_point.lower():
                cmds.matchTransform(grp_offset, "ctrl_EyelidInnerCorner{0}".format(side), pos=True)
                follicle_transform = cmds.rename(cmds.listRelatives(follicle, p=True), "follicle_sphere_eyelidInnerCorner{0}".format(side))
                cmds.select(d=True)
                rib_cjoint = cmds.joint(n="ribbon_cjoint_eyelidInnerCorner{0}".format(side))

            elif "outercorner" in rib_point.lower():
                cmds.matchTransform(grp_offset, "ctrl_EyelidOuterCorner{0}".format(side), pos=True)
                follicle_transform = cmds.rename(cmds.listRelatives(follicle, p=True), "follicle_sphere_eyelidOuterCorner{0}".format(side))
                cmds.select(d=True)
                rib_cjoint = cmds.joint(n="ribbon_cjoint_eyelidOuterCorner{0}".format(side))


            cmds.setAttr(rib_cjoint + ".drawStyle", 2)
            cmds.parent(rib_cjoint, ctrl[0])
            cmds.xform(rib_cjoint, t=(0, 0, 0), ro=(0, 0, 0))
            cmds.makeIdentity(rib_cjoint, a=True, r=True)
            follicle = cmds.listRelatives(follicle_transform)[0]

            if "_l" in rib_point.lower():
                cmds.xform(grp_flip, r=True, ro=(0, 180, 0))

            cmds.parent(follicle_transform, grp_proj_fol)

            cmds.connectAttr(proj_sphere[3][0] + ".outMesh", follicle + ".inputMesh")
            cmds.connectAttr(proj_sphere[3][0] + ".worldMatrix", follicle + ".inputWorldMatrix")
            cmds.connectAttr(follicle + ".outRotate", follicle_transform + ".rotate")
            cmds.connectAttr(follicle + ".outTranslate", follicle_transform + ".translate")
            cmds.setAttr(follicle + ".parameterV", 0.5)
            cmds.setAttr(follicle + ".parameterU", 0.5)

            close_pnt_node = cmds.createNode("closestPointOnMesh", n="closestPointOn" + rib_cjoint)
            cmds.connectAttr(mediator + ".translate", close_pnt_node + ".inPosition")
            cmds.connectAttr(proj_sphere[3][0] + ".worldMesh", close_pnt_node + ".inMesh")
            cmds.connectAttr(proj_sphere[3][0] + ".worldMatrix", close_pnt_node + ".inputMatrix")
            cmds.connectAttr(close_pnt_node + ".result.parameterU", follicle + ".parameterU")
            cmds.connectAttr(close_pnt_node + ".result.parameterV", follicle + ".parameterV")


        cmds.matchTransform("offset_eyelidUpper{0}".format(side), "EyelidUpper" + ctrl_upper_number + "{0}".format(side))
        cmds.matchTransform("offset_eyelidLower{0}".format(side), "EyelidLower" + ctrl_lower_number + "{0}".format(side))
        cmds.matchTransform("offset_eyelidInnerCorner{0}".format(side), "EyelidInnerCorner" + "{0}".format(side))
        cmds.matchTransform("offset_eyelidOuterCorner{0}".format(side), "EyelidOuterCorner" + "{0}".format(side))
        cmds.skinCluster("ribbon_cjoint_eyelidUpper{0}".format(side), "ribbon_cjoint_eyelidLower{0}".format(side),"ribbon_cjoint_eyelidOuterCorner{0}".format(side), "ribbon_cjoint_eyelidInnerCorner{0}".format(side), ribbon[0], tsb=True)

        # attach def joints to ctrl jnts
        for jnt in jnt_list:
            cmds.parent(cmds.pointConstraint("x_" + jnt, jnt), "face_constraints")
            cmds.parent(cmds.orientConstraint("x_" + jnt, jnt), "face_constraints")


def attach_eyelids():
    # make sure brow ctrls are all zeroed out
    ctrl_list = cmds.listRelatives("Eyelids")
    sides = ["_R", "_L"]
    for side in sides:
        ctrl_list.append("eyelidUpper{0}".format(side))
        ctrl_list.append("eyelidLower{0}".format(side))

    for ctrl in ctrl_list:
        cmds.xform("ctrl_" + ctrl, t=(0, 0, 0), ro=(0, 0, 0))

    const_grp = cmds.group(em=True, n="eyelids_ribbon_constraint")
    cmds.parent(const_grp, "face_system")

    rib_jnts = ["eyelidUpper_R", "eyelidUpper_L", "eyelidLower_R", "eyelidLower_L"]
    for jnt in rib_jnts:
        cmds.parent("ribbon_cjoint_" + jnt, "follicle_sphere_" + jnt)
        # cmds.xform(jnt, t=(0, 0, 0), ro=(90, 0, 90))
        cmds.xform("ribbon_cjoint_" + jnt, t=(0, 0, 0))
        # cmds.makeIdentity("ribbon_cjoint_" + jnt, a=True, r=True)
    cmds.select(d=True)

    jnt_list = cmds.listRelatives("Eyelids")

    for jnt in jnt_list:
        const_pnt = cmds.pointConstraint("follicle_" + jnt, "sdk_" + jnt, mo=True)
        const_ori = cmds.orientConstraint("follicle_" + jnt, "sdk_" + jnt, mo=True)
        cmds.parent(const_pnt, const_grp)
        cmds.parent(const_ori, const_grp)
    cmds.select(d=True)


def detach_eyelids():
    # make sure brow ctrls are all zeroed out
    ctrl_list = cmds.listRelatives("Eyelids")
    sides = ["_R", "_L"]
    for side in sides:
        ctrl_list.append("eyelidUpper{0}".format(side))
        ctrl_list.append("eyelidLower{0}".format(side))

    for ctrl in ctrl_list:
        cmds.xform("ctrl_" + ctrl, t=(0, 0, 0), ro=(0, 0, 0))

    # make sure brow ctrls are all zeroed out
    cmds.delete("eyelids_ribbon_constraint")
    cmds.select(d=True)

    rib_jnts = ["eyelidUpper_R", "eyelidUpper_L", "eyelidLower_R", "eyelidLower_L"]
    for jnt in rib_jnts:
        cmds.parent("ribbon_cjoint_" + jnt, "ctrl_" + jnt)
        cmds.xform("ribbon_cjoint_" + jnt, t=(0, 0, 0))
        # cmds.makeIdentity("ribbon_cjoint_" + jnt, a=True, r=True)
    cmds.select(d=True)


