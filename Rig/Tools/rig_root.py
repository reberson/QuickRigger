import maya.cmds as cmds
from Rig.Tools.reference_tools import joint_dictionary_creator
from System.utils import calculatePVPosition as calc_pv
from System.utils import connect_point_constraint, connect_orient_constraint
from definitions import CONTROLS_DIR
from System.import_files import import_ctrl
# TODO: Refactor to Class objects


def create_root_rig(dictionary):

    # main root hierarchy control
    jd = dictionary["Root"]
    grp_offset = cmds.group(n="offset_Root", em=True)
    grp_extra = cmds.group(n="extra_Root", em=True)
    grp_sdk = cmds.group(n="sdk_Root", em=True)
    ctrl = cmds.circle(n="Root_CTRL", r=20, nr=(0, 1, 0))
    cmds.select(d=True)
    jnt = cmds.joint(n="xRoot")
    cmds.setAttr(jnt + ".drawStyle", 2)
    cmds.select(d=True)
    cmds.parent(jnt, ctrl[0])
    cmds.parent(ctrl[0], grp_sdk)
    cmds.parent(grp_sdk, grp_extra)
    cmds.parent(grp_extra, grp_offset)
    cmds.xform(grp_offset, ws=True, t=jd[0], ro=jd[1], roo=jd[2])
    cmds.parent(grp_offset, "root_system")
    root_orient_const = cmds.orientConstraint(jnt, "Root")
    root_point_const = cmds.pointConstraint(jnt, "Root")
    cmds.parent(root_orient_const, "constraints")
    cmds.parent(root_point_const, "constraints")

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

