import maya.cmds as cmds
from scripts.autorigger.shared.utils import calculatePVPosition as calc_pv
from scripts.autorigger.shared.utils import connect_point_constraint, connect_orient_constraint, mirror_object
from scripts.autorigger.resources.definitions import CONTROLS_DIR
from scripts.autorigger.shared.file_handle import file_read_yaml, import_curve
from scripts.autorigger.shared.utils import create_stretch, create_twist_joint

# TODO: Refactor to Class objects
# TODO: Hide all atributes that are not directly controllable
# TODO: Move the roll and heel joints to a reserved space instead of deleting, so that it can be reverted back if the user wants


def create_leg_rig(dict, twist=True):
    # List all necessary joints
    sides = ["_R", "_L"]
    leg_joints = ["Hip_R", "Knee_R", "Ankle_R", "Heel_R", "Toes_R", "Toes_End_R", "FootSideIn_R", "FootSideOut_R",
                  "Hip_L", "Knee_L", "Ankle_L", "Heel_L", "Toes_L", "Toes_End_L", "FootSideIn_L", "FootSideOut_L"]
    leg_joints_fk = ["Hip_R", "Knee_R", "Ankle_R", "Toes_R", "Toes_End_R", "Hip_L", "Knee_L", "Ankle_L", "Toes_L", "Toes_End_L"]
    foot_joints_ik = ["Heel_R", "Toes_R", "Toes_End_R", "FootSideIn_R", "FootSideOut_R","Heel_L", "Toes_L", "Toes_End_L", "FootSideIn_L", "FootSideOut_L"]

    # Create FK rig
    for joint in leg_joints_fk:
        jd = dict[joint]
        grp_offset = cmds.group(n="fk_offset_" + jd[3], em=True)
        grp_sdk = cmds.group(n="fk_sdk_" + jd[3], em=True)
        grp_flip = cmds.group(n="fk_flip_" + jd[3], em=True)

        if "Hip_" in joint:
            ctrl = cmds.rename(import_curve(file_read_yaml(CONTROLS_DIR + "fk_Hip_R.yaml")), "fk_" + jd[3])
        elif "Knee" in joint:
            ctrl = cmds.rename(import_curve(file_read_yaml(CONTROLS_DIR + "fk_Knee_R.yaml")), "fk_" + jd[3])
        elif "Ankle" in joint:
            ctrl = cmds.rename(import_curve(file_read_yaml(CONTROLS_DIR + "fk_Ankle_R.yaml")), "fk_" + jd[3])
        else:
            ctrl = cmds.rename(import_curve(file_read_yaml(CONTROLS_DIR + "fk_Toes_R.yaml")), "fk_" + jd[3])

        if "_L" in joint:
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
    for joint in leg_joints_fk:
        jd = dict[joint]
        if "Hip_" not in joint:
            cmds.parent("fk_offset_" + jd[3], "fkx_" + jd[4])

    # Remove curve shape component from toes end
    cmds.delete(cmds.listRelatives(cmds.ls("fk_Toes_End_R"), s=True))
    cmds.delete(cmds.listRelatives(cmds.ls("fk_Toes_End_L"), s=True))
    cmds.select(d=True)
    # Create FK swing constraint groop
    grp_const_swing = cmds.group(em=True, n="fk_constraint_swing")
    cmds.parent(grp_const_swing, "fk_system")
    cmds.orientConstraint("xSwing", grp_const_swing)
    cmds.pointConstraint("xSwing", grp_const_swing)
    cmds.parent("fk_offset_Hip_R", grp_const_swing)
    cmds.parent("fk_offset_Hip_L", grp_const_swing)

    # Create IK swing constraint groop
    grp_const_swing_ik = cmds.group(em=True, n="ik_constraint_swing")
    cmds.parent(grp_const_swing_ik, "ik_system")
    cmds.orientConstraint("xSwing", grp_const_swing_ik)
    cmds.pointConstraint("xSwing", grp_const_swing_ik)

    # Create IK rig
    for side in sides:
        jnt_hip = cmds.joint(n="ikx_Hip{0}".format(side))
        cmds.setAttr(jnt_hip + ".drawStyle", 2)
        jnt_knee = cmds.joint(n="ikx_Knee{0}".format(side))
        cmds.setAttr(jnt_knee + ".drawStyle", 2)
        jnt_ankle = cmds.joint(n="ikx_Ankle{0}".format(side))
        cmds.setAttr(jnt_ankle + ".drawStyle", 2)
        jnt_toes = cmds.joint(n="ikx_Toes{0}".format(side))
        cmds.setAttr(jnt_toes + ".drawStyle", 2)
        jnt_toesend = cmds.joint(n="ikx_Toes_End{0}".format(side))
        cmds.setAttr(jnt_toesend + ".drawStyle", 2)
        cmds.matchTransform(jnt_hip, "Hip{0}".format(side))
        cmds.matchTransform(jnt_knee, "Knee{0}".format(side))
        cmds.matchTransform(jnt_ankle, "Ankle{0}".format(side))
        cmds.matchTransform(jnt_toes, "Toes{0}".format(side))
        cmds.matchTransform(jnt_toesend, "Toes_End{0}".format(side))
        cmds.select(d=True)
        cmds.makeIdentity(jnt_hip, a=True, r=True)
        cmds.makeIdentity(jnt_knee, a=True, r=True)
        cmds.makeIdentity(jnt_ankle, a=True, r=True)
        cmds.makeIdentity(jnt_toes, a=True, r=True)
        cmds.makeIdentity(jnt_toesend, a=True, r=True)
        ctrl_leg = cmds.rename(import_curve(file_read_yaml(CONTROLS_DIR + "ik_Leg_R.yaml")), "ik_Leg{0}".format(side))
        if "_L" in side:
            mirror_object(ctrl_leg, "x")
            cmds.setAttr(ctrl_leg + ".overrideEnabled", 1)
            cmds.setAttr(ctrl_leg + ".overrideColor", 6)
        else:
            cmds.setAttr(ctrl_leg + ".overrideEnabled", 1)
            cmds.setAttr(ctrl_leg + ".overrideColor", 13)

        cmds.setAttr(ctrl_leg + ".v", lock=True, k=False, cb=False)
        grp_offset_leg = cmds.group(n="ik_offset_Leg{0}".format(side), em=True)
        grp_offset_hip = cmds.group(n="ik_offset_Hip{0}".format(side), em=True)
        cmds.matchTransform(grp_offset_hip, "Hip{0}".format(side))
        cmds.matchTransform(ctrl_leg, "Ankle{0}".format(side), pos=True)
        cmds.matchTransform(grp_offset_leg, "Ankle{0}".format(side), pos=True)
        cmds.parent(jnt_hip, grp_offset_hip)
        cmds.parent(ctrl_leg, grp_offset_leg)
        cmds.parent(grp_offset_hip, grp_const_swing_ik)
        cmds.parent(grp_offset_leg, "ik_constraint_main")

        # Create Foot IK controls
        grp_roll_out = cmds.group(n="ik_offset_FootSideOut{0}".format(side), em=True)
        sdk_roll_out = cmds.group(n="ik_sdk_FootSideOut{0}".format(side), em=True)
        cmds.parent(sdk_roll_out, grp_roll_out)
        cmds.matchTransform(grp_roll_out, "FootSideOut{0}".format(side))

        grp_roll_in = cmds.group(n="ik_offset_FootSideIn{0}".format(side), em=True)
        sdk_roll_in = cmds.group(n="ik_sdk_FootSideIn{0}".format(side), em=True)
        cmds.parent(sdk_roll_in, grp_roll_in)
        cmds.matchTransform(grp_roll_in, "FootSideIn{0}".format(side))

        grp_heel = cmds.group(n="ik_offset_Heel{0}".format(side), em=True)
        sdk_heel = cmds.group(n="ik_sdk_Heel{0}".format(side), em=True)
        ctrl_heel = cmds.rename(import_curve(file_read_yaml(CONTROLS_DIR + "ik_Heel_R.yaml")), "ik_Heel{0}".format(side))
        if "_R" in side:
            cmds.setAttr(ctrl_heel + ".overrideEnabled", 1)
            cmds.setAttr(ctrl_heel + ".overrideColor", 13)
        else:
            cmds.setAttr(ctrl_heel + ".overrideEnabled", 1)
            cmds.setAttr(ctrl_heel + ".overrideColor", 6)
        cmds.setAttr(ctrl_heel + ".v", lock=True, k=False, cb=False)

        cmds.parent(ctrl_heel, sdk_heel)
        cmds.parent(sdk_heel, grp_heel)
        cmds.matchTransform(grp_heel, "Heel{0}".format(side))

        grp_toe = cmds.group(n="ik_offset_Toe{0}".format(side), em=True)
        sdk_toe = cmds.group(n="ik_sdk_Toe{0}".format(side), em=True)
        ctrl_toe = cmds.rename(import_curve(file_read_yaml(CONTROLS_DIR + "ik_Toe{0}.yaml".format(side))),
                               "ik_Toe{0}".format(side))

        if "_R" in side:
            cmds.setAttr(ctrl_toe + ".overrideEnabled", 1)
            cmds.setAttr(ctrl_toe + ".overrideColor", 13)
        else:
            cmds.setAttr(ctrl_toe + ".overrideEnabled", 1)
            cmds.setAttr(ctrl_toe + ".overrideColor", 6)

        cmds.setAttr(ctrl_toe + ".v", lock=True, k=False, cb=False)
        cmds.parent(ctrl_toe, sdk_toe)
        cmds.parent(sdk_toe, grp_toe)
        cmds.matchTransform(grp_toe, "Toes_End{0}".format(side))

        grp_ball = cmds.group(n="ik_offset_FootBall{0}".format(side), em=True)
        sdk_ball = cmds.group(n="ik_sdk_FootBall{0}".format(side), em=True)


        if "_R" in side:
            ctrl_ball = cmds.rename(import_curve(file_read_yaml(CONTROLS_DIR + "ik_FootBall_R.yaml")),
                                    "ik_FootBall{0}".format(side))
            cmds.setAttr(ctrl_ball + ".overrideEnabled", 1)
            cmds.setAttr(ctrl_ball + ".overrideColor", 13)
        else:
            ctrl_ball = cmds.rename(import_curve(file_read_yaml(CONTROLS_DIR + "ik_FootBall_L.yaml")),
                                    "ik_FootBall{0}".format(side))
            cmds.setAttr(ctrl_ball + ".overrideEnabled", 1)
            cmds.setAttr(ctrl_ball + ".overrideColor", 6)

        cmds.setAttr(ctrl_ball + ".v", lock=True, k=False, cb=False)
        cmds.parent(ctrl_ball, sdk_ball)
        cmds.parent(sdk_ball, grp_ball)
        cmds.matchTransform(grp_ball, "Toes{0}".format(side))
        ikh_ball = cmds.ikHandle(sol="ikSCsolver", sj="ikx_Ankle{0}".format(side), ee="ikx_Toes{0}".format(side), n="ikh_FootBall{0}".format(side), p=1, w=1)
        cmds.setAttr(ikh_ball[0] + ".visibility", 0)
        cmds.parent(ikh_ball[0], ctrl_ball)

        grp_flap = cmds.group(n="ik_offset_FootFlap{0}".format(side), em=True)
        sdk_flap = cmds.group(n="ik_sdk_FootFlap{0}".format(side), em=True)

        if "_R" in side:
            ctrl_flap = cmds.rename(import_curve(file_read_yaml(CONTROLS_DIR + "ik_FootFlap_R.yaml")),
                                    "ik_FootFlap{0}".format(side))
            cmds.setAttr(ctrl_flap + ".overrideEnabled", 1)
            cmds.setAttr(ctrl_flap + ".overrideColor", 13)
        else:
            ctrl_flap = cmds.rename(import_curve(file_read_yaml(CONTROLS_DIR + "ik_FootFlap_L.yaml")),
                                    "ik_FootFlap{0}".format(side))
            cmds.setAttr(ctrl_flap + ".overrideEnabled", 1)
            cmds.setAttr(ctrl_flap + ".overrideColor", 6)

        cmds.setAttr(ctrl_flap + ".v", lock=True, k=False, cb=False)
        cmds.parent(ctrl_flap, sdk_flap)
        cmds.parent(sdk_flap, grp_flap)
        cmds.matchTransform(grp_flap, "Toes{0}".format(side))
        ikh_flap = cmds.ikHandle(sol="ikSCsolver", sj="ikx_Toes{0}".format(side), ee="ikx_Toes_End{0}".format(side), n="ikh_FootFlap{0}".format(side), p=0, w=1)
        cmds.setAttr(ikh_flap[0] + ".visibility", 0)
        cmds.parent(ikh_flap[0], ctrl_flap)

        # Reparent Foot controls
        cmds.parent(grp_flap, ctrl_toe)
        cmds.parent(grp_ball, ctrl_toe)
        cmds.parent(grp_toe, ctrl_heel)
        cmds.parent(grp_heel, sdk_roll_in)
        cmds.parent(grp_roll_in, sdk_roll_out)
        cmds.parent(grp_roll_out, ctrl_leg)

        # Foot Sideroll sdk
        cmds.addAttr(ctrl_leg, ln="sideroll", at="float", keyable=True, min=-10, max=10)
        cmds.setDrivenKeyframe("ik_sdk_FootSideOut{0}".format(side), at="rotateZ", cd="ik_Leg{0}.sideroll".format(side), dv=-10, v=60)
        cmds.setDrivenKeyframe("ik_sdk_FootSideOut{0}".format(side), at="rotateZ", cd="ik_Leg{0}.sideroll".format(side), dv=0, v=0)
        cmds.setDrivenKeyframe("ik_sdk_FootSideIn{0}".format(side), at="rotateZ", cd="ik_Leg{0}.sideroll".format(side), dv=0, v=0)
        cmds.setDrivenKeyframe("ik_sdk_FootSideIn{0}".format(side), at="rotateZ", cd="ik_Leg{0}.sideroll".format(side), dv=10, v=-60)

        # Foot Frontroll sdk
        cmds.addAttr(ctrl_leg, ln="frontroll", at="float", keyable=True, min=-10, max=10)
        cmds.setDrivenKeyframe("ik_sdk_Heel{0}".format(side), at="rotateX", cd="ik_Leg{0}.frontroll".format(side), dv=-10, v=60)
        cmds.setDrivenKeyframe("ik_sdk_Heel{0}".format(side), at="rotateX", cd="ik_Leg{0}.frontroll".format(side), dv=0, v=0)

        cmds.setDrivenKeyframe("ik_sdk_FootBall{0}".format(side), at="rotateX", cd="ik_Leg{0}.frontroll".format(side), dv=0, v=0)
        cmds.setDrivenKeyframe("ik_sdk_FootBall{0}".format(side), at="rotateX", cd="ik_Leg{0}.frontroll".format(side), dv=5, v=-30)
        cmds.setDrivenKeyframe("ik_sdk_FootBall{0}".format(side), at="rotateX", cd="ik_Leg{0}.frontroll".format(side), dv=10, v=0)

        cmds.setDrivenKeyframe("ik_sdk_Toe{0}".format(side), at="rotateX", cd="ik_Leg{0}.frontroll".format(side), dv=10, v=-60)
        cmds.setDrivenKeyframe("ik_sdk_Toe{0}".format(side), at="rotateX", cd="ik_Leg{0}.frontroll".format(side), dv=5, v=0)

        # Visual controls for foot sdks
        grp_footdrivers = cmds.group(n="ik_offset_FootDrivers{0}".format(side), em=True)
        grp_frontroll = cmds.group(n="ik_offset_sdk_FootRoll{0}".format(side), em=True)
        # ctrl_frontroll = cmds.circle(n="ik_sdk_FootRoll{0}".format(side), r=2, nr=(1, 0, 0))
        ctrl_frontroll = cmds.rename(import_curve(file_read_yaml(CONTROLS_DIR + "ik_sdk_FootRoll_R.yaml")), "ik_sdk_FootRoll{0}".format(side))
        if "_R" in side:
            cmds.setAttr(ctrl_frontroll + ".overrideEnabled", 1)
            cmds.setAttr(ctrl_frontroll + ".overrideColor", 13)
        else:
            cmds.setAttr(ctrl_frontroll + ".overrideEnabled", 1)
            cmds.setAttr(ctrl_frontroll + ".overrideColor", 6)

        # grp_sideroll = cmds.group(n="ik_offset_sdk_FootSideRoll{0}".format(side), em=True)
        # ctrl_sideroll = cmds.rename(import_curve(file_read_yaml(CONTROLS_DIR + "ik_sdk_FootSideRoll_R.yaml")), "ik_sdk_FootSideRoll{0}".format(side))
        # if "_R" in side:
        #     cmds.setAttr(ctrl_sideroll + ".overrideEnabled", 1)
        #     cmds.setAttr(ctrl_sideroll + ".overrideColor", 13)
        # else:
        #     cmds.setAttr(ctrl_sideroll + ".overrideEnabled", 1)
        #     cmds.setAttr(ctrl_sideroll + ".overrideColor", 6)

        # cmds.parent(ctrl_sideroll, grp_sideroll)
        cmds.parent(ctrl_frontroll, grp_frontroll)
        cmds.parent(grp_frontroll, grp_footdrivers)
        # cmds.parent(grp_sideroll, grp_footdrivers)
        cmds.parent(grp_footdrivers, "drivers_system")
        cmds.matchTransform(grp_footdrivers, "ik_Leg{0}".format(side), pos=True)

        # cmds.matchTransform(grp_frontroll, "FootSideOut{0}".format(side), pos=True)
        cmds.matchTransform(grp_frontroll, "Toes_End{0}".format(side), pos=True)

        cmds.xform(grp_frontroll, r=True, t=(0, 0, 10))
        # if side == "_R":
        #     cmds.xform(grp_frontroll, r=True, t=(-10, 0, 0))
        # else:
        #     cmds.xform(grp_frontroll, r=True, t=(10, 0, 0))

        cmds.setDrivenKeyframe("ik_Leg{0}".format(side), at="frontroll", cd="ik_sdk_FootRoll{0}.tz".format(side), dv=-10,v=-10)
        cmds.setDrivenKeyframe("ik_Leg{0}".format(side), at="frontroll", cd="ik_sdk_FootRoll{0}.tz".format(side), dv=0,v=0)
        cmds.setDrivenKeyframe("ik_Leg{0}".format(side), at="frontroll", cd="ik_sdk_FootRoll{0}.tz".format(side), dv=10, v=10)
        # cmds.matchTransform(grp_sideroll, "Toes_End{0}".format(side), pos=True)
        # cmds.xform(grp_sideroll, r=True, t=(0, 0, 10))

        if side == "_L":
            # cmds.xform(grp_sideroll, r=True, ro=(0, 180, 0))
            # cmds.xform(grp_frontroll, r=True, ro=(0, 180, 0))
            cmds.xform(grp_frontroll, r=True, s=(-1, 1, 1))

        # cmds.setDrivenKeyframe("ik_Leg{0}".format(side), at="sideroll", cd="ik_sdk_FootSideRoll{0}.tx".format(side), dv=-10,v=-10)
        # cmds.setDrivenKeyframe("ik_Leg{0}".format(side), at="sideroll", cd="ik_sdk_FootSideRoll{0}.tx".format(side), dv=0, v=0)
        # cmds.setDrivenKeyframe("ik_Leg{0}".format(side), at="sideroll", cd="ik_sdk_FootSideRoll{0}.tx".format(side), dv=10, v=10)

        cmds.setDrivenKeyframe("ik_Leg{0}".format(side), at="sideroll", cd="ik_sdk_FootRoll{0}.tx".format(side),dv=-10, v=-10)
        cmds.setDrivenKeyframe("ik_Leg{0}".format(side), at="sideroll", cd="ik_sdk_FootRoll{0}.tx".format(side),dv=0, v=0)
        cmds.setDrivenKeyframe("ik_Leg{0}".format(side), at="sideroll", cd="ik_sdk_FootRoll{0}.tx".format(side),dv=10, v=10)

        cmds.orientConstraint("ik_Leg{0}".format(side), grp_footdrivers, mo=True)
        cmds.pointConstraint("ik_Leg{0}".format(side), grp_footdrivers, mo=True)

        # Create IK handle
        ikh = cmds.ikHandle(sol="ikRPsolver", sj="ikx_Hip{0}".format(side), ee="ikx_Ankle{0}".format(side), n="ikh_Leg{0}".format(side), p=2, w=1)
        cmds.parent(ikh[0], ctrl_ball)
        cmds.setAttr(ikh[0] + ".visibility", 0)
        # Create PV
        # pv_leg = cmds.circle(n="pv_Leg{0}".format(side), r=5, nr=(0, 0, 1))
        pv_leg = cmds.rename(import_curve(file_read_yaml(CONTROLS_DIR + "ik_pv.yaml")), "pv_Leg{0}".format(side))
        mirror_object(pv_leg, "z")
        if "_R" in side:
            cmds.setAttr(pv_leg + ".overrideEnabled", 1)
            cmds.setAttr(pv_leg + ".overrideColor", 13)
        else:
            cmds.setAttr(pv_leg + ".overrideEnabled", 1)
            cmds.setAttr(pv_leg + ".overrideColor", 6)

        grp_pv_leg = cmds.group(n="pv_offset_Leg{0}".format(side), em=True)
        cmds.parent(pv_leg, grp_pv_leg)
        pv_pos = calc_pv(["Hip{0}".format(side), "Knee{0}".format(side), "Ankle{0}".format(side)], 70)
        cmds.xform(grp_pv_leg, t=pv_pos, ws=True)
        cmds.parent(grp_pv_leg, "ik_constraint_main")
        # assign constraint pole vector
        cmds.poleVectorConstraint(pv_leg, ikh[0])
        # Create ik/fk switch
        switch_leg = cmds.rename(import_curve(file_read_yaml(CONTROLS_DIR + "ikfk.yaml")), "ikfk_leg{0}".format(side))
        if "_R" in side:
            cmds.setAttr(switch_leg + ".overrideEnabled", 1)
            cmds.setAttr(switch_leg + ".overrideColor", 13)
        else:
            cmds.setAttr(switch_leg + ".overrideEnabled", 1)
            cmds.setAttr(switch_leg + ".overrideColor", 6)
        cmds.setAttr(switch_leg + ".tx", lock=True, k=False, cb=False)
        cmds.setAttr(switch_leg + ".ty", lock=True, k=False, cb=False)
        cmds.setAttr(switch_leg + ".tz", lock=True, k=False, cb=False)
        cmds.setAttr(switch_leg + ".rx", lock=True, k=False, cb=False)
        cmds.setAttr(switch_leg + ".ry", lock=True, k=False, cb=False)
        cmds.setAttr(switch_leg + ".rz", lock=True, k=False, cb=False)
        cmds.setAttr(switch_leg + ".sx", lock=True, k=False, cb=False)
        cmds.setAttr(switch_leg + ".sy", lock=True, k=False, cb=False)
        cmds.setAttr(switch_leg + ".sz", lock=True, k=False, cb=False)

        grp_switch_leg = cmds.group(n="offset_switch_leg{0}".format(side), em=True)
        cmds.matchTransform(grp_switch_leg, "Hip{0}".format(side), pos=True)
        if side == "_R":
            cmds.xform(grp_switch_leg, t=(-20, 0, 0), r=True)
        else:
            cmds.xform(grp_switch_leg, t=(20, 0, 0), r=True)
        cmds.matchTransform(switch_leg, grp_switch_leg)
        cmds.addAttr(switch_leg, longName="ikSwitch", attributeType="double", min=0, max=1, dv=0)
        cmds.setAttr(str(switch_leg) + ".ikSwitch", e=True, channelBox=True)
        cmds.setAttr(str(switch_leg) + ".ikSwitch", 1)
        switch_leg_attr = switch_leg + ".ikSwitch"
        cmds.parent(switch_leg, grp_switch_leg)
        cmds.parent(grp_switch_leg, "follow_ikfk_root")
        # Create unhide attribute
        cmds.addAttr(switch_leg, longName="unhide", attributeType="double", min=0, max=1, dv=0)
        cmds.setAttr(str(switch_leg) + ".unhide", e=True, channelBox=True)
        unhide_attr = switch_leg + ".unhide"

        # Set visibility state for ik fk ctrls
        nd_ikfk_vis_cond = cmds.createNode('condition', ss=True, n="ikfk_leg_vis_cond{0}".format(side))
        nd_ikfk_vis_pma_fk = cmds.createNode('plusMinusAverage', ss=True, n="ikfk_leg_vis_pma_fk{0}".format(side))
        nd_ikfk_vis_pma_ik = cmds.createNode('plusMinusAverage', ss=True, n="ikfk_leg_vis_pma_ik{0}".format(side))
        cmds.setAttr(nd_ikfk_vis_cond + ".colorIfTrueR", 1)
        cmds.setAttr(nd_ikfk_vis_cond + ".colorIfFalseR", 0)

        cmds.connectAttr(switch_leg_attr, nd_ikfk_vis_pma_ik + ".input1D[0]")
        cmds.connectAttr(unhide_attr, nd_ikfk_vis_pma_ik + ".input1D[1]")
        cmds.connectAttr(nd_ikfk_vis_pma_ik + ".output1D", grp_pv_leg + '.visibility')
        cmds.connectAttr(nd_ikfk_vis_pma_ik + ".output1D", grp_offset_leg + '.visibility')
        cmds.connectAttr(nd_ikfk_vis_pma_ik + ".output1D", grp_footdrivers + '.visibility')

        cmds.connectAttr(switch_leg_attr, nd_ikfk_vis_cond + '.firstTerm')
        cmds.connectAttr(nd_ikfk_vis_cond + ".outColorR", nd_ikfk_vis_pma_fk + ".input1D[0]")
        cmds.connectAttr(unhide_attr, nd_ikfk_vis_pma_fk + ".input1D[1]")
        cmds.connectAttr(nd_ikfk_vis_pma_fk + ".output1D", 'fk_offset_Hip{0}.visibility'.format(side))

        # Connect both fk ik rigs to def joints through pont/orient constraint workflow
        leg_list = ["Hip{0}".format(side), "Knee{0}".format(side), "Ankle{0}".format(side), "Toes_End{0}".format(side)]
        for jnt in leg_list:
            point_constraint = connect_point_constraint(jnt, "fkx_" + jnt, "ikx_" + jnt, switch_leg_attr)
            cmds.parent(point_constraint, "constraints")
            orient_constraint = connect_orient_constraint(jnt, "fkx_" + jnt, "ikx_" + jnt, switch_leg_attr)
            cmds.parent(orient_constraint, "constraints")
        cmds.orientConstraint(ctrl_leg, "ikx_Ankle{0}".format(side), mo=True)

        # Do the same thing just for Toes so they won't have point Constraints
        toes_list = ["Toes{0}".format(side)]
        for jnt in toes_list:
            orient_constraint = connect_orient_constraint(jnt, "fkx_" + jnt, "ikx_" + jnt, switch_leg_attr)
            cmds.parent(orient_constraint, "constraints")

        # After the foot rig is built, delete the heel and side ref joints from deform hierarchy
        # cmds.delete("Heel{0}".format(side))
        # cmds.delete("FootSideOut{0}".format(side))
        # cmds.delete("FootSideIn{0}".format(side))

        # Add Twist Joints
        if twist:
            twist_hip = create_twist_joint("Hip{0}".format(side), "Knee{0}".format(side),
                                           "Hip_Twist{0}".format(side))
            cmds.parent(twist_hip[1], "constraints")
            twist_knee = create_twist_joint("Knee{0}".format(side), "Ankle{0}".format(side),
                                            "Knee_Twist{0}".format(side))
            cmds.parent(twist_knee[1], "constraints")
            twist_hip = "Hip_Twist{0}".format(side)
            twist_knee = "Knee_Twist{0}".format(side)
            # Create Stretch
            create_stretch("Knee{0}".format(side), "Hip{0}".format(side), "ikfk_leg{0}".format(side),
                           "fk_offset_Knee{0}".format(side), "ikx_Knee{0}".format(side), twist_hip)
            create_stretch("Ankle{0}".format(side), "Knee{0}".format(side), "ikfk_leg{0}".format(side),
                           "fk_offset_Ankle{0}".format(side), "ikx_Ankle{0}".format(side), twist_knee)
        else:
            # Create Stretch
            create_stretch("Knee{0}".format(side), "Hip{0}".format(side), "ikfk_leg{0}".format(side),
                           "fk_offset_Knee{0}".format(side), "ikx_Knee{0}".format(side))
            create_stretch("Ankle{0}".format(side), "Knee{0}".format(side), "ikfk_leg{0}".format(side),
                           "fk_offset_Ankle{0}".format(side), "ikx_Ankle{0}".format(side))

        # # Create Stretch
        # create_stretch("Knee{0}".format(side), "Hip{0}".format(side), "ikfk_leg{0}".format(side),
        #                "fk_offset_Knee{0}".format(side), "ikx_Knee{0}".format(side), twist_hip)
        # create_stretch("Ankle{0}".format(side), "Knee{0}".format(side), "ikfk_leg{0}".format(side),
        #                "fk_offset_Ankle{0}".format(side), "ikx_Ankle{0}".format(side), twist_knee)

        # # Create blend node to control foot scaling
        # blend_node = cmds.shadingNode("blendColors", n="foot_scale_bc{0}".format(side), au=True)
        # cmds.connectAttr("ik_Leg{0}".format(side) + ".scale", blend_node + ".color1")
        # cmds.connectAttr("fk_Ankle{0}".format(side) + ".scale", blend_node + ".color2")
        # cmds.connectAttr(switch_leg_attr, blend_node + ".blender")
        #
        # # Create foot scale attribute
        # cmds.addAttr(switch_leg, longName='footScale', attributeType='double3')
        # cmds.addAttr(switch_leg, longName='footScalex', attributeType='double', parent='footScale', dv=1)
        # cmds.addAttr(switch_leg, longName='footScaley', attributeType='double', parent='footScale', dv=1)
        # cmds.addAttr(switch_leg, longName='footScalez', attributeType='double', parent='footScale', dv=1)
        #
        # # control the foot scale attribute by the fk foot or ik foot controls
        # cmds.connectAttr(blend_node + ".outputR", switch_leg + '.footScalex')
        # cmds.connectAttr(blend_node + ".outputG", switch_leg + '.footScaley')
        # cmds.connectAttr(blend_node + ".outputB", switch_leg + '.footScalez')
        #
        # # output to ankle and toes joints
        # cmds.connectAttr(switch_leg + '.footScalex', "Ankle{0}".format(side) + ".sx")
        # cmds.connectAttr(switch_leg + '.footScaley', "Ankle{0}".format(side) + ".sy")
        # cmds.connectAttr(switch_leg + '.footScalez', "Ankle{0}".format(side) + ".sz")

        # cmds.connectAttr(switch_leg + '.footScalex', "Toes{0}".format(side) + ".sx")
        # cmds.connectAttr(switch_leg + '.footScaley', "Toes{0}".format(side) + ".sy")
        # cmds.connectAttr(switch_leg + '.footScalez', "Toes{0}".format(side) + ".sz")




        # Create Scale system for Feet
        # Follow Feet Groups
        grp_follow = cmds.group(n="follow_Ankle{0}".format(side), em=True)
        grp_offset = cmds.group(n="scl_offset_Ankle{0}".format(side), em=True)
        grp_sdk = cmds.group(n="scl_sdk_Ankle{0}".format(side), em=True)
        grp_flip = cmds.group(n="scl_flip_Ankle{0}".format(side), em=True)
        scl_ctrl = cmds.rename(import_curve(file_read_yaml(CONTROLS_DIR + "cntrl_stretch_limb.yaml")),
                               "cntrl_scale_Ankle{0}".format(side))

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
        cmds.matchTransform(grp_follow, "Ankle{0}".format(side))

        if "_L" in side:
            cmds.xform(grp_flip, r=True, ro=(180, 0, 0))

        # Make Ankles not inherit transform
        cmds.setAttr("Ankle{0}.inheritsTransform".format(side), 0)
        # create scale constraint
        scale_const_ankle = cmds.scaleConstraint(scl_ctrl, "Ankle{0}".format(side))
        cmds.parent(scale_const_ankle, "constraints")
        scale_const_toes = cmds.scaleConstraint(scl_ctrl, "Toes{0}".format(side))
        cmds.parent(scale_const_toes, "constraints")

        # Make Scale ctrls follow Ankle position
        flw_point_constraint = connect_point_constraint(grp_follow, "fkx_Ankle{0}".format(side),
                                                        "ikx_Ankle{0}".format(side), switch_leg_attr)
        flw_orient_constraint = connect_orient_constraint(grp_follow, "fkx_Ankle{0}".format(side),
                                                          "ikx_Ankle{0}".format(side), switch_leg_attr)