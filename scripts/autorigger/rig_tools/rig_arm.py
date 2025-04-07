import maya.cmds as cmds
from scripts.autorigger.shared.utils import calculatePVPosition as calc_pv
from scripts.autorigger.shared.utils import connect_point_constraint, connect_orient_constraint, mirror_object
from scripts.autorigger.resources.definitions import CONTROLS_DIR
from scripts.autorigger.shared.file_handle import file_read_yaml, import_curve
from scripts.autorigger.shared.utils import create_stretch, create_twist_joint
# TODO: Refactor to Class objects


def create_arm_rig(dict, twist=True):
    # List all necessary joints
    arm_joints = ["Shoulder_R", "Elbow_R", "Wrist_R", "Shoulder_L", "Elbow_L", "Wrist_L"]
    arm_switchers = ["ikfk_arm_R", "ikfk_arm_L"]


    # Create FK rig
    for joint in arm_joints:
        jd = dict[joint]
        grp_offset = cmds.group(n="fk_offset_" + jd[3], em=True)
        grp_sdk = cmds.group(n="fk_sdk_" + jd[3], em=True)
        grp_flip = cmds.group(n="fk_flip_" + jd[3], em=True)
        if "Shoulder_" in joint:
            ctrl = cmds.rename(import_curve(file_read_yaml(CONTROLS_DIR + "fk_Shoulder_R.yaml")), "fk_" + jd[3])
        elif "Elbow_" in joint:
            ctrl = cmds.rename(import_curve(file_read_yaml(CONTROLS_DIR + "fk_Elbow_R.yaml")), "fk_" + jd[3])
        elif "Wrist_" in joint:
            ctrl = cmds.rename(import_curve(file_read_yaml(CONTROLS_DIR + "fk_Wrist_R.yaml")), "fk_" + jd[3])

        if "_l" in joint.lower():
            mirror_object(ctrl, "x")
            mirror_object(ctrl, "y")
            mirror_object(ctrl, "z")
            cmds.setAttr(ctrl + ".overrideEnabled", 1)
            cmds.setAttr(ctrl + ".overrideColor", 6)
        else:
            cmds.setAttr(ctrl + ".overrideEnabled", 1)
            cmds.setAttr(ctrl + ".overrideColor", 13)


        cmds.setAttr(ctrl + ".v", lock=True, k=False, cb=False)
        cmds.select(d=True)
        jnt = cmds.joint(n="fkx_" + jd[3])
        cmds.setAttr(jnt + ".drawStyle", 2)
        cmds.select(d=True)
        cmds.parent(jnt, ctrl)
        cmds.parent(ctrl, grp_flip)
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
        cmds.setAttr("fk_{0}".format(shoulder) + ".global", 1)
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
        ctrl_arm = cmds.rename(import_curve(file_read_yaml(CONTROLS_DIR + "ik_Arm_R.yaml")), "ik_Arm{0}".format(side))
        if "_L" in side:
            mirror_object(ctrl_arm, "x")
            cmds.setAttr(ctrl_arm + ".overrideEnabled", 1)
            cmds.setAttr(ctrl_arm + ".overrideColor", 6)
        else:
            cmds.setAttr(ctrl_arm + ".overrideEnabled", 1)
            cmds.setAttr(ctrl_arm + ".overrideColor", 13)

        cmds.setAttr(ctrl_arm + ".v", lock=True, k=False, cb=False)
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
        cmds.setAttr(ikh[0] + ".visibility", 0)
        # Create PV
        pv_arm = cmds.rename(import_curve(file_read_yaml(CONTROLS_DIR + "ik_pv.yaml")), "pv_Arm{0}".format(side))
        if "_r" in side.lower():
            cmds.setAttr(pv_arm + ".overrideEnabled", 1)
            cmds.setAttr(pv_arm + ".overrideColor", 13)
        else:
            cmds.setAttr(pv_arm + ".overrideEnabled", 1)
            cmds.setAttr(pv_arm + ".overrideColor", 6)
        cmds.setAttr(pv_arm + ".v", lock=True, k=False, cb=False)
        grp_pv_arm = cmds.group(n="pv_offset_Arm{0}".format(side), em=True)
        cmds.parent(pv_arm, grp_pv_arm)
        pv_pos = calc_pv(["Shoulder{0}".format(side), "Elbow{0}".format(side), "Wrist{0}".format(side)], 20)
        cmds.xform(grp_pv_arm, t=pv_pos, ws=True)
        cmds.parent(grp_pv_arm, "ik_constraint_main")
        # assign constraint pole vector
        cmds.poleVectorConstraint(pv_arm, ikh[0])

        # Create ik/fk switch
        switch_arm = cmds.rename(import_curve(file_read_yaml(CONTROLS_DIR + "ikfk.yaml")), "ikfk_arm{0}".format(side))
        cmds.setAttr(switch_arm + ".overrideEnabled", 1)
        if "_R" in side:
            cmds.setAttr(switch_arm + ".overrideColor", 13)
        else:
            cmds.setAttr(switch_arm + ".overrideColor", 6)

        cmds.setAttr(switch_arm + ".tx", lock=True, k=False, cb=False)
        cmds.setAttr(switch_arm + ".ty", lock=True, k=False, cb=False)
        cmds.setAttr(switch_arm + ".tz", lock=True, k=False, cb=False)
        cmds.setAttr(switch_arm + ".rx", lock=True, k=False, cb=False)
        cmds.setAttr(switch_arm + ".ry", lock=True, k=False, cb=False)
        cmds.setAttr(switch_arm + ".rz", lock=True, k=False, cb=False)
        cmds.setAttr(switch_arm + ".sx", lock=True, k=False, cb=False)
        cmds.setAttr(switch_arm + ".sy", lock=True, k=False, cb=False)
        cmds.setAttr(switch_arm + ".sz", lock=True, k=False, cb=False)

        grp_switch_arm = cmds.group(n="offset_switch_arm{0}".format(side), em=True)
        cmds.matchTransform(grp_switch_arm, "Shoulder{0}".format(side), pos=True)
        if side == "_R":
            cmds.xform(grp_switch_arm, t=(-30, 0, 0), r=True)
        else:
            cmds.xform(grp_switch_arm, t=(30, 0, 0), r=True)
        cmds.matchTransform(switch_arm, grp_switch_arm)
        cmds.addAttr(switch_arm, longName="ikSwitch", attributeType="double", min=0, max=1, dv=0)
        cmds.setAttr(str(switch_arm) + ".ikSwitch", e=True, channelBox=True)
        switch_arm_attr = "ikfk_arm{0}.ikSwitch".format(side)
        cmds.parent(switch_arm, grp_switch_arm)
        cmds.parent(grp_switch_arm, "follow_ikfk_root")
        # Create unhide attribute
        cmds.addAttr(switch_arm, longName="unhide", attributeType="double", min=0, max=1, dv=0)
        cmds.setAttr(str(switch_arm) + ".unhide", e=True, channelBox=True)
        unhide_attr = switch_arm + ".unhide"

        # Set visibility state for ik fk ctrls
        nd_ikfk_vis_cond = cmds.createNode('condition', ss=True, n="ikfk_arm_vis_cond{0}".format(side))
        nd_ikfk_vis_pma_fk = cmds.createNode('plusMinusAverage', ss=True, n="ikfk_arm_vis_pma_fk{0}".format(side))
        nd_ikfk_vis_pma_ik = cmds.createNode('plusMinusAverage', ss=True, n="ikfk_arm_vis_pma_ik{0}".format(side))
        cmds.setAttr(nd_ikfk_vis_cond + ".colorIfTrueR", 1)
        cmds.setAttr(nd_ikfk_vis_cond + ".colorIfFalseR", 0)

        cmds.connectAttr(switch_arm_attr, nd_ikfk_vis_pma_ik + ".input1D[0]")
        cmds.connectAttr(unhide_attr, nd_ikfk_vis_pma_ik + ".input1D[1]")
        cmds.connectAttr(nd_ikfk_vis_pma_ik + ".output1D", grp_pv_arm + '.visibility')
        cmds.connectAttr(nd_ikfk_vis_pma_ik + ".output1D", grp_offset_arm + '.visibility')

        cmds.connectAttr(switch_arm_attr, nd_ikfk_vis_cond + '.firstTerm')
        cmds.connectAttr(nd_ikfk_vis_cond + ".outColorR", nd_ikfk_vis_pma_fk + ".input1D[0]")
        cmds.connectAttr(unhide_attr, nd_ikfk_vis_pma_fk + ".input1D[1]")
        cmds.connectAttr(nd_ikfk_vis_pma_fk + ".output1D", 'fk_master_Shoulder{0}.visibility'.format(side))

        # Connect both fk ik rigs to def joints through pont/orient constraint workflow
        arm_list = ["Shoulder{0}".format(side), "Elbow{0}".format(side), "Wrist{0}".format(side)]
        for jnt in arm_list:
            point_constraint = connect_point_constraint(jnt, "fkx_" + jnt, "ikx_" + jnt, switch_arm_attr)
            cmds.parent(point_constraint, "constraints")
            orient_constraint = connect_orient_constraint(jnt, "fkx_" + jnt, "ikx_" + jnt, switch_arm_attr)
            cmds.parent(orient_constraint, "constraints")
        cmds.orientConstraint(ctrl_arm, "ikx_Wrist{0}".format(side), mo=True)

        # Add Twist Joints and Stretch
        if twist:
            twist_shoulder = create_twist_joint("Shoulder{0}".format(side), "Elbow{0}".format(side), "Shoulder_Twist{0}".format(side))
            cmds.parent(twist_shoulder[1], "constraints")
            twist_elbow = create_twist_joint("Elbow{0}".format(side), "Wrist{0}".format(side), "Elbow_Twist{0}".format(side))
            cmds.parent(twist_elbow[1], "constraints")
            twist_shoulder = "Shoulder_Twist{0}".format(side)
            twist_elbow = "Elbow_Twist{0}".format(side)
            # Create Stretch
            create_stretch("Elbow{0}".format(side), "Shoulder{0}".format(side), "ikfk_arm{0}".format(side),
                           "fk_offset_Elbow{0}".format(side), "ikx_Elbow{0}".format(side), twist_shoulder)
            create_stretch("Wrist{0}".format(side), "Elbow{0}".format(side), "ikfk_arm{0}".format(side),
                           "fk_offset_Wrist{0}".format(side), "ikx_Wrist{0}".format(side), twist_elbow)
        else:
            # Create Stretch
            create_stretch("Elbow{0}".format(side), "Shoulder{0}".format(side), "ikfk_arm{0}".format(side),
                           "fk_offset_Elbow{0}".format(side), "ikx_Elbow{0}".format(side))
            create_stretch("Wrist{0}".format(side), "Elbow{0}".format(side), "ikfk_arm{0}".format(side),
                           "fk_offset_Wrist{0}".format(side), "ikx_Wrist{0}".format(side))

        # # Create Stretch
        # create_stretch("Elbow{0}".format(side), "Shoulder{0}".format(side), "ikfk_arm{0}".format(side), "fk_offset_Elbow{0}".format(side), "ikx_Elbow{0}".format(side), twist_shoulder)
        # create_stretch("Wrist{0}".format(side), "Elbow{0}".format(side), "ikfk_arm{0}".format(side), "fk_offset_Wrist{0}".format(side), "ikx_Wrist{0}".format(side), twist_elbow)

        # # Create blend node to control hand scaling
        # blend_node = cmds.shadingNode("blendColors", n="hand_scale_bc{0}".format(side), au=True)
        # cmds.connectAttr("ik_Arm{0}".format(side) + ".scale", blend_node + ".color1")
        # cmds.connectAttr("fk_Wrist{0}".format(side) + ".scale", blend_node + ".color2")
        # cmds.connectAttr(switch_arm_attr, blend_node + ".blender")
        # # Create hand scale attribute
        # cmds.addAttr(switch_arm, longName='handScale', attributeType='double3')
        # cmds.addAttr(switch_arm, longName='handScalex', attributeType='double', parent='handScale', dv=1)
        # cmds.addAttr(switch_arm, longName='handScaley', attributeType='double', parent='handScale', dv=1)
        # cmds.addAttr(switch_arm, longName='handScalez', attributeType='double', parent='handScale', dv=1)
        #
        # # control the hand scale attribute by the fk hand or ik hand controls
        # cmds.connectAttr(blend_node + ".outputR", switch_arm + '.handScalex')
        # cmds.connectAttr(blend_node + ".outputG", switch_arm + '.handScaley')
        # cmds.connectAttr(blend_node + ".outputB", switch_arm + '.handScalez')
        #
        # # output to wrist joint
        # cmds.connectAttr(switch_arm + '.handScalex', "Wrist{0}".format(side) + ".sx")
        # cmds.connectAttr(switch_arm + '.handScaley', "Wrist{0}".format(side) + ".sy")
        # cmds.connectAttr(switch_arm + '.handScalez', "Wrist{0}".format(side) + ".sz")

        # Create Scale system for Hands
        # Follow Hands Groups
        grp_follow = cmds.group(n="follow_Wrist{0}".format(side), em=True)
        grp_offset = cmds.group(n="scl_offset_Wrist{0}".format(side), em=True)
        grp_sdk = cmds.group(n="scl_sdk_Wrist{0}".format(side), em=True)
        grp_flip = cmds.group(n="scl_flip_Wrist{0}".format(side), em=True)
        scl_ctrl = cmds.rename(import_curve(file_read_yaml(CONTROLS_DIR + "cntrl_stretch_limb.yaml")),
                               "cntrl_scale_Wrist{0}".format(side))

        if "_R" in side:
            cmds.setAttr(scl_ctrl + ".overrideEnabled", 1)
            cmds.setAttr(scl_ctrl + ".overrideColor", 31)
        elif "_L" in side:
            cmds.setAttr(scl_ctrl + ".overrideEnabled", 1)
            cmds.setAttr(scl_ctrl + ".overrideColor", 18)
        cmds.setAttr(scl_ctrl + ".tx", lock=True, k=False, cb=False)
        cmds.setAttr(scl_ctrl + ".ty", lock=True, k=False, cb=False)
        cmds.setAttr(scl_ctrl + ".tz", lock=True, k=False, cb=False)
        cmds.setAttr(scl_ctrl + ".rx", lock=True, k=False, cb=False)
        cmds.setAttr(scl_ctrl + ".ry", lock=True, k=False, cb=False)
        cmds.setAttr(scl_ctrl + ".rz", lock=True, k=False, cb=False)

        cmds.parent(scl_ctrl, grp_flip)
        cmds.parent(grp_flip, grp_sdk)
        cmds.parent(grp_sdk, grp_offset)
        cmds.parent(grp_offset, grp_follow)
        cmds.parent(grp_follow, "scale_system")
        cmds.matchTransform(grp_follow, "Wrist{0}".format(side))

        if "_L" in side:
            cmds.xform(grp_flip, r=True, ro=(180, 0, 0))

        # Make Wrists not inherit transform
        cmds.setAttr("Wrist{0}.inheritsTransform".format(side), 0)
        # create scale constraint
        scale_const = cmds.scaleConstraint(scl_ctrl, "Wrist{0}".format(side))
        cmds.parent(scale_const, "constraints")

        # Make Scale ctrls follow hand position
        flw_point_constraint = connect_point_constraint(grp_follow, "fkx_Wrist{0}".format(side), "ikx_Wrist{0}".format(side), switch_arm_attr)
        flw_orient_constraint = connect_orient_constraint(grp_follow, "fkx_Wrist{0}".format(side), "ikx_Wrist{0}".format(side), switch_arm_attr)

