import maya.cmds as cmds
from Rig.Tools.reference_tools import joint_dictionary_creator
from definitions import CONTROLS_DIR
from System.file_handle import import_ctrl
from System.utils import connect_point_constraint, connect_orient_constraint, mirror_object
from definitions import CONTROLS_DIR
from System.file_handle import file_read_yaml, import_curve

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
        # ctrl = cmds.circle(n="fk_" + jd[3], r=10, nr=(0, 1, 0))
        if "Neck" in joint:
            ctrl = cmds.rename(import_curve(file_read_yaml(CONTROLS_DIR + "fk_Neck.yaml")), "fk_" + jd[3])
        else:
            ctrl = cmds.rename(import_curve(file_read_yaml(CONTROLS_DIR + "fk_Head.yaml")), "fk_" + jd[3])

        cmds.setAttr(ctrl + ".overrideEnabled", 1)
        cmds.setAttr(ctrl + ".overrideColor", 17)
        cmds.select(d=True)
        jnt = cmds.joint(n="fkx_" + jd[3])
        cmds.setAttr(jnt + ".drawStyle", 2)
        cmds.select(d=True)
        cmds.parent(jnt, ctrl)
        cmds.parent(ctrl, grp_flip)
        cmds.parent(grp_flip, grp_sdk)
        cmds.parent(grp_sdk, grp_offset)
        cmds.xform(grp_offset, ws=True, t=jd[0], ro=jd[1], roo=jd[2])
        cmds.orientConstraint(jnt, joint)
        cmds.orientConstraint(jnt, joint)
        # Create additional head groups for global follow
        if "Head" in joint:
            grp_master = cmds.group(n="fk_master_" + jd[3], em=True)
            grp_fl_global = cmds.group(n="fk_follow_global_" + jd[3], em=True)
            grp_fl_neck = cmds.group(n="fk_follow_neck_" + jd[3], em=True)
            grp_fl = cmds.group(n="fk_follow_" + jd[3], em=True)
            cmds.parent(grp_fl, grp_master)
            cmds.parent(grp_fl_global, grp_master)
            cmds.parent(grp_fl_neck, grp_master)
            cmds.xform(grp_master, ws=True, t=jd[0], ro=jd[1], roo=jd[2])
            cmds.parent(grp_offset, grp_fl)
            # Create global Attr and nodes to head

            # Create Global system groups
            grp_gl_off_head = cmds.group(em=True, n="global_offset_" + jd[3])
            grp_gl_head = cmds.group(em=True, n="global_" + jd[3])
            cmds.parent(grp_gl_head, grp_gl_off_head)
            cmds.xform(grp_gl_off_head, ws=True, t=jd[0], ro=jd[1], roo=jd[2])
            cmds.parent(grp_gl_off_head, "global_constraint_main")
            # Create global attribute on fk head ctrl
            cmds.addAttr("fk_" + jd[3], longName="global", attributeType="double", min=0, max=1, dv=0)
            cmds.setAttr("fk_" + jd[3] + ".global", e=True, channelBox=True)
            cmds.setAttr("fk_" + jd[3] + ".global", 1)
            # Constrain the fk shoulder to both follow chest and follow global
            connect_orient_constraint(grp_fl, grp_fl_neck, grp_fl_global, "fk_" + jd[3] + ".global")
            # cmds.parent("fk_offset_{0}".format(shoulder), grp_fk_shld_flw)
            # Constraint global to globalsystem and follow neck to neck joint
            cmds.orientConstraint(grp_gl_head, grp_fl_global, mo=True, n="follow_global_" + jd[3])
            cmds.orientConstraint("Neck_M", grp_fl_neck, mo=True, n="follow_neck_" + jd[3])

    cmds.select(d=True)
    cmds.parent("fk_offset_Neck_M", "fk_constraint_chest")
    cmds.parent("fk_master_Head_M", "fkx_Neck_M")



