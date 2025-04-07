import maya.cmds as cmds
from Rig.Tools.reference_tools import joint_dictionary_creator
from System.utils import connect_point_constraint, connect_orient_constraint
from definitions import CONTROLS_DIR
from System.import_files import import_ctrl

# TODO: Refactor to Class objects
# TODO: Add support for twist joint

def create_neck_rig(dict):
    # List all necessary joints
    neck_joints = ["Neck_M", "Head_M"]

    # Create FK rig
    for joint in neck_joints:
        jd = dict[joint]
        grp_offset = cmds.group(n="fk_offset_" + jd[3], em=True)
        grp_sdk = cmds.group(n="fk_sdk_" + jd[3], em=True)
        grp_flip = cmds.group(n="fk_flip_" + jd[3], em=True)
        ctrl = cmds.circle(n="fk_" + jd[3], r=10, nr=(0, 1, 0))
        cmds.select(d=True)
        jnt = cmds.joint(n="fkx_" + jd[3])
        cmds.setAttr(jnt + ".drawStyle", 2)
        cmds.select(d=True)
        cmds.parent(jnt, ctrl[0])
        cmds.parent(ctrl[0], grp_flip)
        cmds.parent(grp_flip, grp_sdk)
        cmds.parent(grp_sdk, grp_offset)
        cmds.xform(grp_offset, ws=True, t=jd[0], ro=jd[1], roo=jd[2])
        cmds.orientConstraint(jnt, joint)
        cmds.orientConstraint(jnt, joint)

    # Parent FK linearly
    for joint in neck_joints:
        jd = dict[joint]
        if "Neck_M" not in joint:
            cmds.parent("fk_offset_" + jd[3], "fkx_" + jd[4])
    cmds.select(d=True)
    cmds.parent("fk_offset_Neck_M", "fk_constraint_chest")

