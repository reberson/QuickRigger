import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
from System.utils import create_ribbon_flat, create_lattice_plane, create_ribbon, joint_list


# TODO: create a toggle for follicle visibility
# TODO: change the code to be number agnostic of joints.
# TODO: Change the way the follicle controls attach to the far left, far right and center joints

def create_brow(dict):
    grp_ctrl = cmds.group(em=True, n="brow_control_group")
    cmds.matchTransform(grp_ctrl, "Facial")
    cmds.parent(grp_ctrl, "face_constrain_head")

    jnt_list = joint_list("Brows", "Brow_M", first_half="_r", second_half="_l")
    first_jnt = jnt_list[0]
    last_jnt = jnt_list[len(jnt_list) - 1]

    # create base controls
    for jnt in jnt_list:
        jd = dict[jnt]
        grp_offset = cmds.group(em=True, n="offset_" + jnt)
        grp_flip = cmds.group(em=True, n="flip_" + jnt)
        grp_sdk = cmds.group(em=True, n="sdk_" + jnt)
        # ctrl = cmds.circle(n="ctrl_" + jnt, cy=1, r=0.75, nr=(0, 1, 0))
        if "_R" in jnt:
            ctrl = cmds.circle(n="ctrl_" + jnt, cy=1, r=0.75, nr=(0, 1, 0))
        elif "_L" in jnt:
            ctrl = cmds.circle(n="ctrl_" + jnt, cy=-1, r=0.75, nr=(0, 1, 0))
        else:
            ctrl = cmds.circle(n="ctrl_" + jnt, cy=1, r=0.75, nr=(0, 1, 0))

        cmds.select(d=True)
        xjnt = cmds.joint(n="x_" + jnt)
        cmds.setAttr(xjnt + ".radius", 0.5)
        cmds.select(d=True)
        cmds.setAttr(xjnt + ".drawStyle", 2)

        cmds.parent(xjnt, ctrl)
        cmds.parent(ctrl, grp_flip)
        cmds.parent(grp_flip, grp_sdk)
        cmds.parent(grp_sdk, grp_offset)
        cmds.parent(grp_offset, grp_ctrl)
        cmds.xform(grp_offset, ws=True, t=jd[0], ro=jd[1], roo=jd[2])
        if "_L" in jnt:
            cmds.xform(grp_flip, r=True, ro=(0, 180, 0))

    # ribbon = create_ribbon_flat("Brow_4_L", "Brow_4_R", "Brow_M", "ribbon_brow", jnt_list)
    ribbon = create_ribbon("ribbon_brow", jnt_list)
    param_u_step = ribbon[3]
    cmds.parent(ribbon[0], grp_ctrl)
    cmds.parent(ribbon[1], grp_ctrl)

    proj_plane = create_lattice_plane("Brow_M", 40, 40, "proj_plane_forehead")
    cmds.parent(proj_plane[0], "face_constrain_head")
    # Create the primary controls
    rib_point_list = ["brow_R", "brow_M", "brow_L"]
    for rib_point in rib_point_list:
        grp_offset = cmds.group(em=True, n="offset_" + rib_point)
        grp_flip = cmds.group(em=True, n="flip_" + rib_point)
        grp_sdk = cmds.group(em=True, n="sdk_" + rib_point)
        if "_L" in rib_point:
            ctrl = cmds.circle(n="ctrl_" + rib_point, cy=-1, r=1, nr=(0, 1, 0))
        else:
            ctrl = cmds.circle(n="ctrl_" + rib_point, cy=1, r=1, nr=(0, 1, 0))
        mediator = cmds.group(em=True, n="mediator_" + rib_point)

        cmds.parent(ctrl, grp_sdk)
        cmds.parent(grp_sdk, grp_flip)
        cmds.parent(grp_flip, grp_offset)
        cmds.parent(grp_offset, grp_ctrl)
        cmds.xform(grp_offset, ro=(90, 0, 90))
        cmds.parent(mediator, "face_mediators")
        cmds.pointConstraint(ctrl, mediator)
        # cmds.orientConstraint(ctrl, rib_cjoint)
        follicle = cmds.createNode("follicle")
        if rib_point == "brow_R":
            # cmds.matchTransform(grp_offset, "follicle_Brow_4_R", pos=True)
            cmds.matchTransform(grp_offset, "follicle_" + jnt_list[0], pos=True)
            follicle_transform = cmds.rename(cmds.listRelatives(follicle, p=True), "follicle_plane_brow_R")
            cmds.select(d=True)
            rib_cjoint = cmds.joint(n="ribbon_cjoint_brow_R")
        elif rib_point == "brow_M":
            cmds.matchTransform(grp_offset, "follicle_Brow_M", pos=True)
            follicle_transform = cmds.rename(cmds.listRelatives(follicle, p=True), "follicle_plane_brow_M")
            cmds.select(d=True)
            rib_cjoint = cmds.joint(n="ribbon_cjoint_brow_M")
        elif rib_point == "brow_L":
            cmds.matchTransform(grp_offset, "follicle_" + last_jnt, pos=True)
            follicle_transform = cmds.rename(cmds.listRelatives(follicle, p=True), "follicle_plane_brow_L")
            cmds.select(d=True)
            rib_cjoint = cmds.joint(n="ribbon_cjoint_brow_L")
            cmds.xform(grp_flip, r=True, ro=(0, 180, 0))

        cmds.setAttr(rib_cjoint + ".drawStyle", 2)
        cmds.parent(rib_cjoint, ctrl)
        cmds.xform(rib_cjoint, t=(0, 0, 0), ro=(0, 0, 0))
        cmds.makeIdentity(rib_cjoint, a=True, r=True)
        follicle = cmds.listRelatives(follicle_transform)[0]

        # follicle = cmds.createNode("follicle", n="brow_follicle")
        # follicle_transform = cmds.listRelatives(follicle, p=True)
        cmds.parent(follicle_transform, "face_system")

        cmds.connectAttr(proj_plane[3][0] + ".outMesh", follicle + ".inputMesh")
        cmds.connectAttr(proj_plane[3][0] + ".worldMatrix", follicle + ".inputWorldMatrix")
        cmds.connectAttr(follicle + ".outRotate", follicle_transform + ".rotate")
        cmds.connectAttr(follicle + ".outTranslate", follicle_transform + ".translate")
        cmds.setAttr(follicle + ".parameterV", 0.5)
        cmds.setAttr(follicle + ".parameterU", 0.5)

        close_pnt_node = cmds.createNode("closestPointOnMesh", n="closestPointOn" + rib_cjoint)
        cmds.connectAttr(mediator + ".translate", close_pnt_node + ".inPosition")
        cmds.connectAttr(proj_plane[3][0] + ".worldMesh", close_pnt_node + ".inMesh")
        cmds.connectAttr(proj_plane[3][0] + ".worldMatrix", close_pnt_node + ".inputMatrix")
        cmds.connectAttr(close_pnt_node + ".result.parameterU", follicle + ".parameterU")
        cmds.connectAttr(close_pnt_node + ".result.parameterV", follicle + ".parameterV")

        # cmds.parent(rib_cjoint, follicle_transform)
        # cmds.xform(rib_cjoint, t=(0, 0, 0), ro=(90, 0, 90))
        # cmds.makeIdentity(rib_cjoint, a=True, r=True)

    cmds.matchTransform("offset_brow_R", jnt_list[0])
    cmds.matchTransform("offset_brow_M", "Brow_M")
    cmds.matchTransform("offset_brow_L", last_jnt)
    cmds.skinCluster("ribbon_cjoint_brow_R", "ribbon_cjoint_brow_M", "ribbon_cjoint_brow_L", ribbon[0], tsb=True)

    # attach def joints to ctrl jnts
    for jnt in jnt_list:
        cmds.parent(cmds.pointConstraint("x_" + jnt, jnt), "face_constraints")
        cmds.parent(cmds.orientConstraint("x_" + jnt, jnt), "face_constraints")


def attach_brow():
    # make sure brow ctrls are all zeroed out
    # ctrl_list = ['Brow_4_R', 'Brow_3_R', 'Brow_2_R', 'Brow_1_R', 'Brow_M', 'Brow_1_L', 'Brow_2_L', 'Brow_3_L',
    #              'Brow_4_L', "brow_R", "brow_M", "brow_L"]
    ctrl_list = joint_list("Brows", "Brow_M")
    ctrl_list.append("brow_R")
    ctrl_list.append("brow_M")
    ctrl_list.append("brow_L")
    for ctrl in ctrl_list:
        cmds.xform("ctrl_" + ctrl, t=(0, 0, 0), ro=(0, 0, 0))

    const_grp = cmds.group(em=True, n="brow_ribbon_constraint")
    cmds.parent(const_grp, "face_system")

    rib_jnts = ["brow_R", "brow_M", "brow_L"]
    for jnt in rib_jnts:
        cmds.parent("ribbon_cjoint_" + jnt, "follicle_plane_" + jnt)
        # cmds.xform(jnt, t=(0, 0, 0), ro=(90, 0, 90))
        cmds.xform("ribbon_cjoint_" + jnt, t=(0, 0, 0))
        # cmds.makeIdentity("ribbon_cjoint_" + jnt, a=True, r=True)
    cmds.select(d=True)

    # jnt_list = ['Brow_4_R', 'Brow_3_R', 'Brow_2_R', 'Brow_1_R', 'Brow_M', 'Brow_1_L', 'Brow_2_L', 'Brow_3_L',
    #             'Brow_4_L']
    jnt_list = joint_list("Brows", "Brow_M")

    for jnt in jnt_list:
        const_pnt = cmds.pointConstraint("follicle_" + jnt, "sdk_" + jnt, mo=True)
        const_ori = cmds.orientConstraint("follicle_" + jnt, "sdk_" + jnt, mo=True)
        cmds.parent(const_pnt, const_grp)
        cmds.parent(const_ori, const_grp)
    cmds.select(d=True)


def detach_brow():
    # ctrl_list = ['Brow_4_R', 'Brow_3_R', 'Brow_2_R', 'Brow_1_R', 'Brow_M', 'Brow_1_L', 'Brow_2_L', 'Brow_3_L',
    #              'Brow_4_L', "brow_R", "brow_M", "brow_L"]
    ctrl_list = joint_list("Brows", "Brow_M")
    ctrl_list.append("brow_R")
    ctrl_list.append("brow_M")
    ctrl_list.append("brow_L")
    for ctrl in ctrl_list:
        cmds.xform("ctrl_" + ctrl, t=(0, 0, 0), ro=(0, 0, 0))
    # make sure brow ctrls are all zeroed out
    cmds.delete("brow_ribbon_constraint")
    cmds.select(d=True)

    rib_jnts = ["brow_R", "brow_M", "brow_L"]
    for jnt in rib_jnts:
        cmds.parent("ribbon_cjoint_" + jnt, "ctrl_" + jnt)
        cmds.xform("ribbon_cjoint_" + jnt, t=(0, 0, 0))
        # cmds.makeIdentity("ribbon_cjoint_" + jnt, a=True, r=True)
    cmds.select(d=True)


