import maya.cmds as cmds
from Rig.Tools.reference_tools import joint_dictionary_creator
from System.utils import calculatePVPosition as calc_pv
from System.utils import connect_point_constraint, connect_orient_constraint
from definitions import CONTROLS_DIR
from System.import_files import import_ctrl

# TODO: Refactor to Class objects

def create_arm_rig(dict):
    # Create FK system group
    # fk_grp = cmds.group(em=True, n="fk_system")
    # cmds.parent(fk_grp, "rig")
    # List all necessary joints
    arm_joints = ["Shoulder_R", "Elbow_R", "Wrist_R", "Shoulder_L", "Elbow_L", "Wrist_L"]
    arm_switchers = ["ikfk_arm_R", "ikfk_arm_L"]

    # Create FK rig
    for joint in arm_joints:
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

    # Parent FK linearly
    for joint in arm_joints:
        jd = dict[joint]
        if "Shoulder_" not in joint:
            cmds.parent("fk_offset_" + jd[3], "fkx_" + jd[4])

    cmds.select(d=True)

    # Shoulder additional groups
    shoulder_sides = ["Shoulder_R", "Shoulder_L"]
    for shoulder in shoulder_sides:
        grp_fk_shld_master = cmds.group(em=True, n="fk_master_{0}".format(shoulder))
        grp_fk_shld_chest = cmds.group(em=True, n="fk_follow_chest_{0}".format(shoulder))
        grp_fk_shld_global = cmds.group(em=True, n="fk_follow_global_{0}".format(shoulder))
        grp_fk_shld_flw = cmds.group(em=True, n="fk_follow_{0}".format(shoulder))
        cmds.parent(grp_fk_shld_chest, grp_fk_shld_master)
        cmds.parent(grp_fk_shld_global, grp_fk_shld_master)
        cmds.parent(grp_fk_shld_flw, grp_fk_shld_master)
        cmds.matchTransform(grp_fk_shld_master, shoulder)
        # Create Global system groups
        grp_gl_off_shld = cmds.group(em=True, n="global_offset_{0}".format(shoulder))
        grp_gl_shld = cmds.group(em=True, n="global_{0}".format(shoulder))
        cmds.parent(grp_gl_shld, grp_gl_off_shld)
        cmds.matchTransform(grp_gl_off_shld, shoulder)
        cmds.parent(grp_gl_off_shld, "global_constraint_main")
        # Create global attribute on fk shoulder ctrl
        cmds.addAttr("fk_{0}".format(shoulder), longName="global", attributeType="double", min=0, max=1, dv=0)
        cmds.setAttr("fk_{0}".format(shoulder) + ".global", e=True, channelBox=True)
        # Constrain the fk shoulder to both follow chest and follow global
        connect_orient_constraint(grp_fk_shld_flw, grp_fk_shld_chest, grp_fk_shld_global, "fk_" + shoulder + ".global")
        cmds.parent("fk_offset_{0}".format(shoulder), grp_fk_shld_flw)
        # Constraint global to globalsystem and follow chest to chest joint
        cmds.orientConstraint(grp_gl_shld, grp_fk_shld_global, mo=True, n="follow_global_{0}".format(shoulder))
        cmds.orientConstraint("Chest_M", grp_fk_shld_chest, mo=True, n="follow_chest_{0}".format(shoulder))

    cmds.parent("fk_master_Shoulder_R", "fkx_Scapula_R")
    cmds.parent("fk_master_Shoulder_L", "fkx_Scapula_L")



    # Create IK rig
    sides = ["_R", "_L"]
    for side in sides:
        # IK Arm
        grp_const_scapula = cmds.group(em=True, n="ik_constraint_scapula{0}".format(side))
        cmds.orientConstraint("Scapula{0}".format(side), grp_const_scapula)
        cmds.pointConstraint("Scapula{0}".format(side), grp_const_scapula)
        jnt_shoulder = cmds.joint(n="ikx_Shoulder{0}".format(side))
        cmds.setAttr(jnt_shoulder + ".drawStyle", 2)
        jnt_elbow = cmds.joint(n="ikx_Elbow{0}".format(side))
        cmds.setAttr(jnt_elbow + ".drawStyle", 2)
        jnt_wrist = cmds.joint(n="ikx_Wrist{0}".format(side))
        cmds.setAttr(jnt_wrist + ".drawStyle", 2)
        cmds.matchTransform(jnt_shoulder, "Shoulder{0}".format(side))
        cmds.matchTransform(jnt_elbow, "Elbow{0}".format(side))
        cmds.matchTransform(jnt_wrist, "Wrist{0}".format(side))
        cmds.select(d=True)
        cmds.makeIdentity(jnt_shoulder, a=True, r=True)
        cmds.makeIdentity(jnt_elbow, a=True, r=True)
        cmds.makeIdentity(jnt_wrist, a=True, r=True)
        ctrl_arm = import_ctrl(CONTROLS_DIR + 'square.ma', "ik_Arm{0}".format(side))
        grp_offset_arm = cmds.group(n="ik_offset_Arm{0}".format(side), em=True)
        grp_offset_shoulder = cmds.group(n="ik_offset_Shoulder{0}".format(side), em=True)
        cmds.matchTransform(grp_offset_shoulder, "Shoulder{0}".format(side))
        cmds.matchTransform(ctrl_arm, "Wrist{0}".format(side), pos=True)
        cmds.matchTransform(grp_offset_arm, "Wrist{0}".format(side), pos=True)
        cmds.parent(jnt_shoulder, grp_offset_shoulder)
        cmds.parent(ctrl_arm, grp_offset_arm)
        cmds.parent(grp_offset_shoulder, grp_const_scapula)
        cmds.parent(grp_offset_arm, "ik_constraint_main")
        cmds.parent(grp_const_scapula, "ik_system")
        # Create IK handle
        ikh = cmds.ikHandle(sol="ikRPsolver", sj="ikx_Shoulder{0}".format(side), ee="ikx_Wrist{0}".format(side), n="ikh_Arm{0}".format(side), ap=True, w=1)
        cmds.parent(ikh[0], ctrl_arm)
        # Create PV
        pv_arm = cmds.circle(n="pv_Arm{0}".format(side), r=5, nr=(0, 0, 1))
        grp_pv_arm = cmds.group(n="pv_offset_Arm{0}".format(side), em=True)
        cmds.parent(pv_arm[0], grp_pv_arm)
        pv_pos = calc_pv(["Shoulder{0}".format(side), "Elbow{0}".format(side), "Wrist{0}".format(side)], 20)
        cmds.xform(grp_pv_arm, t=pv_pos, ws=True)
        cmds.parent(grp_pv_arm, "ik_constraint_main")
        # assign constraint pole vector
        cmds.poleVectorConstraint(pv_arm, ikh[0])
        # Create ik/fk switch
        switch_arm = cmds.circle(n="ikfk_arm{0}".format(side), nr=(0, 1, 0), c=(0, 0, 0), r=2)
        grp_switch_arm = cmds.group(n="offset_switch_arm{0}".format(side), em=True)
        cmds.matchTransform(grp_switch_arm, "Shoulder{0}".format(side), pos=True)
        if side == "_R":
            cmds.xform(grp_switch_arm, t=(-30, 0, 0), r=True)
        else:
            cmds.xform(grp_switch_arm, t=(30, 0, 0), r=True)
        cmds.matchTransform(switch_arm, grp_switch_arm)
        cmds.addAttr(switch_arm, longName="ikSwitch", attributeType="double", min=0, max=1, dv=0)
        cmds.setAttr(str(switch_arm[0]) + ".ikSwitch", e=True, channelBox=True)
        switch_arm_attr = "ikfk_arm{0}.ikSwitch".format(side)
        cmds.parent(switch_arm[0], grp_switch_arm)
        cmds.parent(grp_switch_arm, "follow_ikfk_main")
        # Connect both fk ik rigs to def joints through pont/orient constraint workflow
        arm_list = ["Shoulder{0}".format(side), "Elbow{0}".format(side), "Wrist{0}".format(side)]
        for jnt in arm_list:
            point_constraint = connect_point_constraint(jnt, "fkx_" + jnt, "ikx_" + jnt, switch_arm_attr)
            cmds.parent(point_constraint, "constraints")
            orient_constraint = connect_orient_constraint(jnt, "fkx_" + jnt, "ikx_" + jnt, switch_arm_attr)
            cmds.parent(orient_constraint, "constraints")
        cmds.orientConstraint(ctrl_arm, "ikx_Wrist{0}".format(side), mo=True)




