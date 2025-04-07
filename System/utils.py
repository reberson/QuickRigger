import maya.OpenMaya as OpenMaya
import maya.cmds as cmds
from System.file_handle import file_read_yaml, import_curve
from definitions import CONTROLS_DIR
import pymel.core as pm


def mirror_object(object_tr, axis):
    if axis.lower() == "x":
        cmds.xform(object_tr, r=True, s=(-1, 1, 1))
    elif axis.lower() == "y":
        cmds.xform(object_tr, r=True, s=(1, -1, 1))
    elif axis.lower() == "z":
        cmds.xform(object_tr, r=True, s=(1, 1, -1))
    else:
        cmds.error("Invalid axis", n=True)
    cmds.makeIdentity(object_tr, a=True, s=True)


def mirror_joint(first_joint):
    """Mirrors the joint and gives proper naming"""
    if "_L" in str(first_joint):
        cmds.mirrorJoint(first_joint, mb=True, myz=True, sr=["_L", "_R"])
    elif "_l" in str(first_joint):
        cmds.mirrorJoint(first_joint, mb=True, myz=True, sr=["_l", "_r"])
    elif "_R" in str(first_joint):
        cmds.mirrorJoint(first_joint, mb=True, myz=True, sr=["_R", "_L"])
    elif "_r" in str(first_joint):
        cmds.mirrorJoint(first_joint, mb=True, myz=True, sr=["_r", "_l"])
    else:
        cmds.error(f"The joint {first_joint} is not eligible to be mirrored")
    cmds.select(d=True)


def calculatePVPosition(jnts, distance):
    start = cmds.xform(jnts[0], q=True, ws=True, t=True)
    mid = cmds.xform(jnts[1], q=True, ws=True, t=True)
    end = cmds.xform(jnts[2], q=True, ws=True, t=True)
    startV = OpenMaya.MVector(start[0], start[1], start[2])
    midV = OpenMaya.MVector(mid[0], mid[1], mid[2])
    endV = OpenMaya.MVector(end[0], end[1], end[2])
    startEnd = endV - startV
    startMid = (midV - startV) * distance
    dotP = startMid * startEnd
    proj = float(dotP) / float(startEnd.length())
    startEndN = startEnd.normal()
    projV = startEndN * proj
    arrowV = startMid - projV
    arrowV *= 0.5
    finalV = arrowV + midV
    return ([finalV.x, finalV.y, finalV.z])


# def connect_bc(def_jnt, fk_jnt, ik_jnt, attribute_name, switch_name):
#     # Create blend color nodes and attach to the target attribute
#     constraints = []
#     bcNodeT = cmds.shadingNode("blendColors", asUtility=True, n='bcNodeT_switch_' + switch_name)
#     cmds.connectAttr(attribute_name, bcNodeT + '.blender')
#     bcNodeR = cmds.shadingNode("blendColors", asUtility=True, n='bcNodeR_switch_' + switch_name)
#     cmds.connectAttr(attribute_name, bcNodeR + '.blender')
#     bcNodeS = cmds.shadingNode("blendColors", asUtility=True, n='bcNodeS_switch_' + switch_name)
#     cmds.connectAttr(attribute_name, bcNodeS + '.blender')
#     constraints.append([bcNodeT, bcNodeR, bcNodeS])
#
#     # Input FK jnt
#     cmds.connectAttr(fk_jnt + '.translate', bcNodeT + '.color1')
#     cmds.connectAttr(fk_jnt + '.rotate', bcNodeR + '.color1')
#     cmds.connectAttr(fk_jnt + '.scale', bcNodeS + '.color1')
#
#     # Input IK jnt
#     cmds.connectAttr(ik_jnt + '.translate', bcNodeT + '.color2')
#     cmds.connectAttr(ik_jnt + '.rotate', bcNodeR + '.color2')
#     cmds.connectAttr(ik_jnt + '.scale', bcNodeS + '.color2')
#
#     # Output Deform jnt
#     cmds.connectAttr(bcNodeT + '.output', def_jnt + '.translate')
#     cmds.connectAttr(bcNodeR + '.output', def_jnt + '.rotate')
#     cmds.connectAttr(bcNodeS + '.output', def_jnt + '.scale')
#
#     return constraints


def connect_point_constraint(def_jnt, fk_jnt, ik_jnt, attribute):
    # creates point constraint between 2 sources to 1 target (ik/fk to def)
    point_constraint = cmds.pointConstraint(ik_jnt, fk_jnt, def_jnt)

    # connect custom attribute to first source weight
    cmds.connectAttr(attribute, point_constraint[0] + "." + ik_jnt + "W0")

    # create reverse node for ik source
    reverse_node = cmds.createNode('reverse', n="reverse_" + fk_jnt)
    cmds.connectAttr(attribute, reverse_node + ".input.inputX")
    cmds.connectAttr(reverse_node + ".output.outputX", point_constraint[0] + "." + fk_jnt + "W1")
    return point_constraint


def connect_orient_constraint(def_jnt, fk_jnt, ik_jnt, attribute):
    # creates orient constraint between 2 sources to 1 target (ik/fk to def)
    orient_constraint = cmds.orientConstraint(ik_jnt, fk_jnt, def_jnt)

    # connect custom attribute to first source weight
    cmds.connectAttr(attribute, orient_constraint[0] + "." + ik_jnt + "W0")

    # create reverse node for ik source
    reverse_node = cmds.createNode('reverse', n="reverse_" + fk_jnt)
    cmds.connectAttr(attribute, reverse_node + ".input.inputX")
    cmds.connectAttr(reverse_node + ".output.outputX", orient_constraint[0] + "." + fk_jnt + "W1")
    return orient_constraint


# Todo: Find a way to make sure the Left twist joints are on the oposite orientation. Might not brake as is, but it's good to set
def create_twist_joint(parent_jnt, child_jnt, name):
    start = cmds.xform(parent_jnt, q=True, ws=True, t=True)
    start_rot = cmds.xform(parent_jnt, q=True, ws=True, ro=True)
    start_roo = cmds.xform(parent_jnt, q=True, ws=True, roo=True)
    end = cmds.xform(child_jnt, q=True, ws=True, t=True)
    start_v = OpenMaya.MVector(start[0], start[1], start[2])
    end_v = OpenMaya.MVector(end[0], end[1], end[2])
    length_v = (end_v - start_v).length()

    cmds.select(d=True)
    twist_jnt = cmds.joint(n=name)
    cmds.select(d=True)
    cmds.parent(twist_jnt, parent_jnt)
    cmds.xform(twist_jnt, t=(0, 0, 0), ro=(0, 0, 0))

    if "_L" in name:
        cmds.delete(cmds.aimConstraint(child_jnt, twist_jnt, aim=(0, -1, 0)))
        length_v *= -1
    else:
        cmds.delete(cmds.aimConstraint(child_jnt, twist_jnt, aim=(0, 1, 0)))
    cmds.makeIdentity(twist_jnt, a=True, r=True, jo=False)

    cmds.xform(twist_jnt, t=(0, length_v / 2, 0), os=True)
    cmds.xform(twist_jnt, roo=start_roo)
    cmds.makeIdentity(twist_jnt, a=True, r=True, jo=False)

    twist_cont = cmds.parentConstraint(parent_jnt, child_jnt, twist_jnt, w=0.5, sr=["x", "z"], st=["x", "y", "z"])
    cmds.setAttr(twist_cont[0] + ".interpType", 0)
    cmds.setAttr(twist_cont[0] + "." + parent_jnt + "W0", 0.6)
    cmds.setAttr(twist_cont[0] + "." + child_jnt + "W1", 0.4)
    return twist_jnt, twist_cont[0]


def create_stretch(stretch_jnt, scale_jnt, att_holder, grp_offset, ikx_jnt, twist_jnt=None):
    # concatenate attribute names
    stretch_name = stretch_jnt + "_Stretch"
    diameter_name = scale_jnt + "_Diameter"

    # STRETCH
    # creates attributes
    cmds.addAttr(att_holder, longName=stretch_name, attributeType="float", dv=0)
    offset_value = (cmds.xform(grp_offset, q=True, t=True, r=True))[1]
    cmds.setAttr(str(att_holder) + "." + stretch_name, e=True, channelBox=True, k=True)
    stretch_att = att_holder + "." + stretch_name
    # creates multiply divide node
    nd_md = cmds.createNode('multiplyDivide', ss=True, n=stretch_name + "_node_md")
    # the below value is only for Left side
    if "_L" in stretch_jnt:
        cmds.setAttr(nd_md + ".input2X", -1)
    # create plus minus average node
    nd_pma = cmds.createNode('plusMinusAverage', ss=True, n=stretch_name + "_node_pma")
    cmds.setAttr(nd_pma + ".operation", 1)
    cmds.setAttr(nd_pma + ".input1D[1]", offset_value)
    # connect attributes
    cmds.connectAttr(stretch_att, nd_md + '.input1X')
    cmds.connectAttr(nd_md + ".outputX", nd_pma + '.input1D[0]')
    cmds.connectAttr(nd_pma + '.output1D', grp_offset + ".ty")
    cmds.connectAttr(nd_pma + '.output1D', ikx_jnt + ".ty")

    # twist jnt
    if twist_jnt:
        offset_value_twist = (cmds.xform(twist_jnt, q=True, t=True, r=True))[1]
        nd_md_twist = cmds.createNode('multiplyDivide', ss=True, n=stretch_name + "_node_md")
        cmds.setAttr(nd_md_twist + ".input2X", 0.5)
        nd_pma_twist = cmds.createNode('plusMinusAverage', ss=True, n=stretch_name + "_node_pma_twist")
        cmds.setAttr(nd_pma_twist + ".operation", 1)
        cmds.setAttr(nd_pma_twist + ".input1D[1]", offset_value_twist)
        cmds.connectAttr(nd_md + ".outputX", nd_md_twist + '.input1X')
        cmds.connectAttr(nd_md_twist + ".outputX", nd_pma_twist + '.input1D[0]')
        cmds.connectAttr(nd_pma_twist + '.output1D', twist_jnt + ".ty")

    # DIAMETER
    # creates attributes
    cmds.addAttr(att_holder, longName=diameter_name, attributeType="float", dv=1)
    cmds.setAttr(str(att_holder) + "." + diameter_name, e=True, channelBox=True, k=True)
    scale_att = att_holder + "." + diameter_name
    # connect attributes
    cmds.connectAttr(scale_att, scale_jnt + ".sx")
    cmds.connectAttr(scale_att, scale_jnt + ".sz")

    # create visual controls for stretch and attach to each limb
    stretch_grp = "stretch_system"
    off_grp = cmds.group(em=True, n="st_offset_" + stretch_jnt)
    sdk_grp = cmds.group(em=True, n="st_sdk_" + stretch_jnt)
    flip_grp = cmds.group(em=True, n="st_flip_" + stretch_jnt)
    st_ctrl = cmds.rename(import_curve(file_read_yaml(CONTROLS_DIR + "cntrl_stretch_limb.yaml")), "cntrl_stretch_" + scale_jnt)

    if "_R" in stretch_jnt:
        cmds.setAttr(st_ctrl + ".overrideEnabled", 1)
        cmds.setAttr(st_ctrl + ".overrideColor", 31)
    elif "_L" in stretch_jnt:
        cmds.setAttr(st_ctrl + ".overrideEnabled", 1)
        cmds.setAttr(st_ctrl + ".overrideColor", 18)
    else:
        cmds.setAttr(st_ctrl + ".overrideEnabled", 1)
        cmds.setAttr(st_ctrl + ".overrideColor", 21)

    cmds.setAttr(st_ctrl + ".tx", lock=True, k=False, cb=False)
    cmds.setAttr(st_ctrl + ".tz", lock=True, k=False, cb=False)
    cmds.setAttr(st_ctrl + ".rx", lock=True, k=False, cb=False)
    cmds.setAttr(st_ctrl + ".ry", lock=True, k=False, cb=False)
    cmds.setAttr(st_ctrl + ".rz", lock=True, k=False, cb=False)

    cmds.parent(st_ctrl, flip_grp)
    cmds.parent(flip_grp, sdk_grp)
    cmds.parent(sdk_grp, off_grp)
    cmds.parent(off_grp, stretch_grp)
    cmds.matchTransform(off_grp, scale_jnt)
    cmds.pointConstraint(scale_jnt, off_grp)
    cmds.orientConstraint(scale_jnt, off_grp)
    cmds.connectAttr(st_ctrl + ".ty", stretch_att)
    cmds.connectAttr(st_ctrl + ".sx", scale_att)

    if "_L" in stretch_jnt:
        cmds.xform(flip_grp, r=True, ro=(180, 0, 0))


def create_ribbon(ribbon_name, transform_list, duplicated=None, direction=(0, -1, 0), reverse=False):
    point_list = []
    for index, jnt in enumerate(transform_list):
        point = cmds.xform(jnt, q=True, ws=True, t=True)
        vector = OpenMaya.MVector(point[0], point[1], point[2])
        # add twice the value of the first and last, so it has one span for each joint position
        if index == 0:
            point_list.append(point)
        elif index == len(transform_list) - 1:
            point_list.append(point)
        point_list.append(point)
    new_curve = cmds.curve(p=point_list)
    cmds.reverseCurve(new_curve)
    extruded_ribbon = cmds.extrude(new_curve, et=0, l=0.2, po=0, d=direction, n=ribbon_name)
    cmds.delete(new_curve)
    ribbon_shape = cmds.listRelatives(extruded_ribbon[0])
    if reverse:
        cmds.reverseSurface(ribbon_shape)

    steps = len(transform_list) - 1
    param_u_step = 1 / steps
    param_u_step_sum = 0
    ribbon_follicle_grp = cmds.group(em=True, n="follicles_" + ribbon_name)
    ribbon = cmds.listRelatives(ribbon_shape, p=True)
    for item in reversed(transform_list):
        follicle = cmds.createNode("follicle")
        if duplicated:
            if duplicated in item.lower():
                follicle_transform = cmds.rename(cmds.listRelatives(follicle, p=True), "follicle_" + item + "_copy")
            else:
                follicle_transform = cmds.rename(cmds.listRelatives(follicle, p=True), "follicle_" + item)
        else:
            follicle_transform = cmds.rename(cmds.listRelatives(follicle, p=True), "follicle_" + item)

        follicle = cmds.listRelatives(follicle_transform)[0]
        cmds.connectAttr(ribbon_shape[0] + ".local", follicle + ".inputSurface")
        cmds.connectAttr(ribbon_shape[0] + ".worldMatrix", follicle + ".inputWorldMatrix")
        cmds.connectAttr(follicle + ".outRotate", follicle_transform + ".rotate")
        cmds.connectAttr(follicle + ".outTranslate", follicle_transform + ".translate")
        cmds.setAttr(follicle + ".parameterV", 0)
        cmds.setAttr(follicle + ".parameterU", param_u_step_sum)
        param_u_step_sum += param_u_step
        cmds.parent(follicle_transform, ribbon_follicle_grp)
        cmds.select(d=True)

    return ribbon, ribbon_follicle_grp, ribbon_shape, param_u_step


def create_ribbon_closed(ribbon_name, transform_list, center_jnt, left_side=False):
    point_list = []
    for index, jnt in enumerate(transform_list):
        point = cmds.xform(jnt, q=True, ws=True, t=True)
        vector = OpenMaya.MVector(point[0], point[1], point[2])
        point_list.append(point)
    new_curve = cmds.curve(p=point_list)
    if left_side == False:
        cmds.reverseCurve(new_curve)

    # get center joint point and apply to the curve pivot
    center_point = cmds.xform(center_jnt, q=True, t=True, ws=True)
    cmds.xform(new_curve, piv=center_point)

    cmds.closeCurve(new_curve, rpo=True, bki=True, p=0, ps=0)
    curve_dupli = cmds.duplicate(new_curve)
    cmds.xform(curve_dupli, cp=True)
    cmds.xform(curve_dupli, s=(0.9, 0.9, 1))
    cmds.select(d=True)
    extruded_ribbon = cmds.loft(curve_dupli, new_curve, n=ribbon_name)

    cmds.xform(extruded_ribbon[0], piv=center_point)

    cmds.delete(new_curve)
    cmds.delete(curve_dupli)

    ribbon_shape = cmds.listRelatives(extruded_ribbon[0])
    steps = len(transform_list) - 1
    param_u_step = 1 / steps
    param_u_step_sum = 0
    ribbon_follicle_grp = cmds.group(em=True, n="follicles_" + ribbon_name)
    ribbon = cmds.listRelatives(ribbon_shape, p=True)
    # ribs = pm.ls(ribbon, type=pm.nt.NurbsSurface)[0]
    # ribs = cmds.listRelatives(ribbon, type="nurbsSurface", ad=True)[0]
    ribs = pm.listRelatives(ribbon, type=pm.nt.NurbsSurface)[0]

    # TODO: try to replace by cmds. Check if the "closestPoint" is a node that can be added as "setAttr".

    for item in reversed(transform_list):
        check = pm.xform(item, t=True, q=True, ws=True)
        point, u, v = ribs.closestPoint(check, space='world')
        v /= len(transform_list)
        follicle = cmds.createNode("follicle")
        follicle_transform = cmds.rename(cmds.listRelatives(follicle, p=True), "follicle_" + item)
        follicle = cmds.listRelatives(follicle_transform)[0]
        cmds.connectAttr(ribbon_shape[0] + ".local", follicle + ".inputSurface")
        cmds.connectAttr(ribbon_shape[0] + ".worldMatrix", follicle + ".inputWorldMatrix")
        cmds.connectAttr(follicle + ".outRotate", follicle_transform + ".rotate")
        cmds.connectAttr(follicle + ".outTranslate", follicle_transform + ".translate")
        cmds.setAttr(follicle + ".parameterU", 0.5)
        cmds.setAttr(follicle + ".parameterV", v)
        v += param_u_step
        param_u_step_sum += param_u_step
        cmds.parent(follicle_transform, ribbon_follicle_grp)
        cmds.select(d=True)

    return ribbon, ribbon_follicle_grp, ribbon_shape, param_u_step


def create_lattice_plane(origin_transform, height, width, name):
    grp = cmds.group(em=True, n="group_" + name)
    proj_plane = cmds.polyPlane(n=name, ax=(0, 0, 1), h=height, w=width, sh=80, sw=80)
    proj_plane_shape = cmds.listRelatives(proj_plane[0])
    # cmds.delete(proj_plane, constructionHistory=True)
    proj_plane_lattice = cmds.lattice(proj_plane[0], dv=(5, 5, 2), oc=True, n=name + "_")
    cmds.parent(proj_plane[0], grp)
    cmds.parent(proj_plane_lattice[1], grp)
    cmds.parent(proj_plane_lattice[2], grp)
    cmds.matchTransform(grp, origin_transform, pos=True)
    return grp, proj_plane, proj_plane_lattice, proj_plane_shape


def create_lattice_sphere(origin_transform, radius, name):
    grp = cmds.group(em=True, n="group_" + name)
    proj_sphere = cmds.polySphere(n=name, ax=(1, 0, 0), r=radius, sa=32, sh=32)

    proj_sphere_shape = cmds.listRelatives(proj_sphere[0])
    # cmds.delete(proj_sphere, constructionHistory=True)
    proj_sphere_lattice = cmds.lattice(proj_sphere[0], dv=(2, 2, 2), oc=True, n=name + "_")
    cmds.parent(proj_sphere[0], grp)
    cmds.parent(proj_sphere_lattice[1], grp)
    cmds.parent(proj_sphere_lattice[2], grp)
    cmds.matchTransform(grp, origin_transform, pos=True)
    return grp, proj_sphere, proj_sphere_lattice, proj_sphere_shape


def joint_list(parent, middle_joint=None, last_joint=None, first_half=None, second_half=None):
    jnts = cmds.listRelatives(parent)
    jnt_list_first_half = []
    jnt_list_second_half = []

    for jnt in jnts:
        if first_half in jnt.lower():
            jnt_list_first_half.append(jnt)
        elif second_half in jnt.lower():
            jnt_list_second_half.append(jnt)

    jnt_list_first_half.sort(reverse=True)
    jnt_list_second_half.sort()

    jnt_list = []

    for jnt in jnt_list_first_half:
        jnt_list.append(jnt)
    if middle_joint:
        jnt_list.append(middle_joint)
    for jnt in jnt_list_second_half:
        jnt_list.append(jnt)
    if last_joint:
        jnt_list.append(last_joint)
    first_jnt = jnt_list[0]
    last_jnt = len(jnt_list) - 1

    return jnt_list
