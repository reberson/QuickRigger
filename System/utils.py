import maya.OpenMaya as OpenMaya
import maya.cmds as cmds


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


def calculatePVPosition(jnts, distance):
    from maya import cmds, OpenMaya
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


def connect_bc(def_jnt, fk_jnt, ik_jnt, attribute_name, switch_name):
    # Create blend color nodes and attach to the target attribute
    constraints = []
    bcNodeT = cmds.shadingNode("blendColors", asUtility=True, n='bcNodeT_switch_' + switch_name)
    cmds.connectAttr(attribute_name, bcNodeT + '.blender')
    bcNodeR = cmds.shadingNode("blendColors", asUtility=True, n='bcNodeR_switch_' + switch_name)
    cmds.connectAttr(attribute_name, bcNodeR + '.blender')
    bcNodeS = cmds.shadingNode("blendColors", asUtility=True, n='bcNodeS_switch_' + switch_name)
    cmds.connectAttr(attribute_name, bcNodeS + '.blender')
    constraints.append([bcNodeT, bcNodeR, bcNodeS])

    # Input FK jnt
    cmds.connectAttr(fk_jnt + '.translate', bcNodeT + '.color1')
    cmds.connectAttr(fk_jnt + '.rotate', bcNodeR + '.color1')
    cmds.connectAttr(fk_jnt + '.scale', bcNodeS + '.color1')

    # Input IK jnt
    cmds.connectAttr(ik_jnt + '.translate', bcNodeT + '.color2')
    cmds.connectAttr(ik_jnt + '.rotate', bcNodeR + '.color2')
    cmds.connectAttr(ik_jnt + '.scale', bcNodeS + '.color2')

    # Output Deform jnt
    cmds.connectAttr(bcNodeT + '.output', def_jnt + '.translate')
    cmds.connectAttr(bcNodeR + '.output', def_jnt + '.rotate')
    cmds.connectAttr(bcNodeS + '.output', def_jnt + '.scale')

    return constraints


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
