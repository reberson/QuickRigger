import maya.cmds as cmds
from Rig.Tools.reference_tools import joint_dictionary_creator
from System.utils import calculatePVPosition as calc_pv
from System.utils import connect_point_constraint, connect_orient_constraint
from definitions import CONTROLS_DIR
from System.file_handle import file_read_yaml, import_curve
# TODO: Refactor to Class objects


def create_root_rig(dictionary):

    # main root hierarchy control
    jd = dictionary["Root"]
    grp_offset = cmds.group(n="offset_Root", em=True)
    grp_extra = cmds.group(n="extra_Root", em=True)
    grp_sdk = cmds.group(n="sdk_Root", em=True)
    # ctrl = cmds.circle(n="Root_CTRL", r=20, nr=(0, 1, 0))
    ctrl = cmds.rename(import_curve(file_read_yaml(CONTROLS_DIR + "Root.yaml")), "Root_CTRL")
    cmds.setAttr(ctrl + ".overrideEnabled", 1)
    cmds.setAttr(ctrl + ".overrideColor", 17)
    cmds.select(d=True)
    jnt_root = cmds.joint(n="xRoot")
    cmds.setAttr(jnt_root + ".drawStyle", 2)
    cmds.select(d=True)
    cmds.parent(jnt_root, ctrl)
    cmds.parent(ctrl, grp_sdk)
    cmds.parent(grp_sdk, grp_extra)
    cmds.parent(grp_extra, grp_offset)
    cmds.xform(grp_offset, ws=True, t=jd[0], ro=jd[1], roo=jd[2])
    cmds.parent(grp_offset, "root_system")
    # Create hip swing structure
    grp_swing_offset = cmds.group(n="offset_Swing", em=True)
    grp_swing_extra = cmds.group(n="extra_Swing", em=True)
    grp_swing_sdk = cmds.group(n="sdk_Swing", em=True)
    # ctrl_swing = cmds.circle(n="Swing_CTRL", r=20, nr=(0, 0, 1))
    ctrl_swing = cmds.rename(import_curve(file_read_yaml(CONTROLS_DIR + "Swing.yaml")), "Swing_CTRL")
    cmds.setAttr(ctrl_swing + ".overrideEnabled", 1)
    cmds.setAttr(ctrl_swing + ".overrideColor", 17)
    cmds.select(d=True)
    jnt_swing = cmds.joint(n="xSwing")
    cmds.setAttr(jnt_swing + ".drawStyle", 2)
    cmds.select(d=True)
    cmds.parent(jnt_swing, ctrl_swing)
    cmds.parent(ctrl_swing, grp_swing_sdk)
    cmds.parent(grp_swing_sdk, grp_swing_extra)
    cmds.parent(grp_swing_extra, grp_swing_offset)
    cmds.xform(grp_swing_offset, ws=True, t=jd[0], ro=jd[1], roo=jd[2])
    cmds.parent(grp_swing_offset, "root_system")
    # constraint root jnt to swing
    root_orient_const = cmds.orientConstraint(jnt_swing, "Root")
    root_point_const = cmds.pointConstraint(jnt_swing, "Root")
    cmds.parent(root_orient_const, "constraints")
    cmds.parent(root_point_const, "constraints")
    # Constraint the swing to root ctrl
    cmds.orientConstraint(jnt_root, grp_swing_extra)
    cmds.pointConstraint(jnt_root, grp_swing_extra)

    # Set the ik fk follow root groups to follow the newly created "xRoot"
    cmds.orientConstraint(jnt_root, "follow_ikfk_root")
    cmds.pointConstraint(jnt_root, "follow_ikfk_root")

    # additional hierarchy to follow main
    grp_cnst_main = cmds.group(n="follow_main_Root", em=True)
    grp_center = cmds.group(n="center_Root", em=True)
    cmds.matchTransform(grp_center, "Root")
    cmds.parent(grp_center, grp_cnst_main)
    cmds.parent(grp_cnst_main, "root_system")
    cmds.orientConstraint("Main", grp_cnst_main)
    cmds.pointConstraint("Main", grp_cnst_main)

    # make root ctrl extra grp follow main follower
    cmds.orientConstraint(grp_center, grp_extra)
    cmds.pointConstraint(grp_center, grp_extra)

