import maya.cmds as cmds
from Rig.Tools.reference_tools import joint_dictionary_creator
from System.utils import connect_point_constraint, connect_orient_constraint
from definitions import CONTROLS_DIR
from System.import_files import import_ctrl

# TODO: Refactor to Class objects
# TODO: toggle visibility for ik fk

def create_torso_rig(dict):
    # List all necessary joints
    torso_joints = ["Spine1_M", "Spine2_M", "Chest_M"]
    scapula_joints = ["Scapula_R", "Scapula_L"]

    # Create FK rig
    for joint in torso_joints:
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
    for joint in torso_joints:
        jd = dict[joint]
        if "Spine1_M" not in joint:
            cmds.parent("fk_offset_" + jd[3], "fkx_" + jd[4])
    cmds.select(d=True)

    # Create constrained groups
    grp_cst_chest = cmds.group(em=True, n="fk_constraint_chest")
    cmds.pointConstraint("Chest_M", grp_cst_chest)
    cmds.orientConstraint("Chest_M", grp_cst_chest)
    cmds.parent(grp_cst_chest, "fk_system")

    grp_cst_root = cmds.group(em=True, n="fk_constraint_root")
    cmds.pointConstraint("Root", grp_cst_root)
    cmds.orientConstraint("Root", grp_cst_root)
    cmds.parent(grp_cst_root, "fk_system")

    cmds.parent("fk_offset_Spine1_M", grp_cst_root)

    # Scapula Controls - They need special attention
    for joint in scapula_joints:
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
        cmds.parent(grp_offset, grp_cst_chest)

    # constrain the actual scapula def joints
    sc_ori_r = cmds.orientConstraint("fk_Scapula_R", "Scapula_R", mo=True)
    sc_poi_r = cmds.pointConstraint("fk_Scapula_R", "Scapula_R", mo=True)
    sc_ori_l = cmds.orientConstraint("fk_Scapula_L", "Scapula_L", mo=True)
    sc_poi_l = cmds.pointConstraint("fk_Scapula_L", "Scapula_L", mo=True)
    cmds.parent(sc_ori_r, "constraints")
    cmds.parent(sc_poi_r, "constraints")
    cmds.parent(sc_ori_l, "constraints")
    cmds.parent(sc_poi_l, "constraints")

    # Create IK rig
    torso_ik_joints = ["Spine1_M", "Spine2_M", "Chest_M", "Neck_M"]
    for joint in torso_ik_joints:
        jd = dict[joint]
        cmds.select(d=True)
        ik_jnt = cmds.joint(n="ikx_" + jd[3])
        cmds.setAttr(ik_jnt + ".drawStyle", 2)
        cmds.xform(ik_jnt, ws=True, t=jd[0], ro=jd[1], roo=jd[2])
        cmds.select(d=True)

    cmds.select(d=True)
    # Parent IK linearly
    for joint in torso_ik_joints:
        jd = dict[joint]
        if "Spine1_M" not in joint:
            cmds.parent("ikx_" + jd[3], "ikx_" + jd[4])
    cmds.select(d=True)

    # create ik_constraint root
    ik_const_root = cmds.group(n="ik_constraint_root", em=True)
    ik_const_main = cmds.group(n="ik_constraint_main", em=True)
    ik_grp_spine_jnts = cmds.group(n="ik_spine_joints", em=True)
    ik_spine_ctrls = cmds.group(em=True, n="ik_spine_controls")
    cmds.parent(ik_grp_spine_jnts, ik_const_root)
    cmds.parent(ik_spine_ctrls, ik_const_root)
    cmds.pointConstraint("Root", ik_const_root)
    cmds.orientConstraint("Root", ik_const_root)
    cmds.pointConstraint("Main", ik_const_main)
    cmds.orientConstraint("Main", ik_const_main)
    cmds.parent(ik_const_root, "ik_system")
    cmds.parent(ik_const_main, "ik_system")
    cmds.parent("ikx_Spine1_M", ik_grp_spine_jnts)

    # Create IK spline handle
    ikh_spine = cmds.ikHandle(sol="ikSplineSolver", sj="ikx_Spine1_M", ee="ikx_Neck_M", n="ikh_Spine", ccv=True,
                              pcv=False, scv=False, tws="linear", roc=False, ap=True, w=1)
    cmds.parent(ikh_spine[0], ik_const_root)
    ikh_curve = ikh_spine[2]
    ikh_curve = cmds.rename(ikh_curve, "ikh_spine_curve")
    cmds.parent(ikh_curve, ik_const_main)
    # connect invers matrix from follow main group to offset parent materix curve
    cmds.connectAttr(ik_const_main + ".worldInverseMatrix", ikh_curve + ".offsetParentMatrix")

    # Create ik controls
    torso_ik_refs = ["Spine1_M", "Chest_M", "Neck_M"]
    for joint in torso_ik_refs:
        jd = dict[joint]
        grp_offset = cmds.group(n="ik_offset_" + jd[3], em=True)
        grp_sdk = cmds.group(n="ik_sdk_" + jd[3], em=True)

        ctrl = cmds.circle(n="ik_" + jd[3], r=15, nr=(0, 1, 0))
        cmds.select(d=True)
        jnt = cmds.joint(n="bind_" + jd[3])
        cmds.setAttr(jnt + ".drawStyle", 2)
        cmds.select(d=True)
        cmds.parent(jnt, ctrl[0])
        cmds.parent(ctrl[0], grp_sdk)
        cmds.parent(grp_sdk, grp_offset)
        cmds.xform(grp_offset, ws=True, t=jd[0], ro=jd[1], roo=jd[2])
        cmds.parent(grp_offset, ik_spine_ctrls)

    # Bind spine curve to ik controls
    cmds.select(d=True)
    cmds.skinCluster("bind_Spine1_M", "bind_Chest_M", "bind_Neck_M", ikh_curve, tsb=True)

    # Connect Roll and Twist attributes from ik handle to the ik controls
    cmds.connectAttr("ik_Spine1_M.rotateY", "ikh_Spine.roll")
    spine_mult_node = cmds.createNode('multiplyDivide', ss=True, n='spine_ik_multi')
    spine_pma_node = cmds.createNode('plusMinusAverage', ss=True, n='spine_ik_pma')

    cmds.setAttr(spine_mult_node + '.input2X', -1)
    cmds.connectAttr("ik_Spine1_M.rotateY", spine_mult_node + '.input1X')
    cmds.connectAttr(spine_mult_node + '.outputX', spine_pma_node + ".input1D[0]")
    cmds.connectAttr("ik_Chest_M.rotateY", spine_pma_node + ".input1D[1]")
    cmds.connectAttr("ik_Neck_M.rotateY", spine_pma_node + ".input1D[2]")
    cmds.connectAttr(spine_pma_node + ".output1D", "ikh_Spine.twist")

    # Create ik/fk switch
    switch_torso = cmds.circle(n="ikfk_torso", nr=(0, 1, 0), c=(0, 0, 0), r=2)
    cmds.addAttr(switch_torso, longName="ikSwitch", attributeType="double", min=0, max=1, dv=0)
    cmds.setAttr(str(switch_torso[0]) + ".ikSwitch", e=True, channelBox=True)
    switch_torso_attr = switch_torso[0] + ".ikSwitch"
    grp_switch_torso = cmds.group(n="offset_ikfk_torso", em=True)
    grp_switch_follow_main = cmds.group(n="follow_ikfk_torso", em=True)
    cmds.parent(switch_torso[0], grp_switch_torso)
    cmds.parent(grp_switch_torso, grp_switch_follow_main)
    cmds.parent(grp_switch_follow_main, "fkik_system")
    cmds.orientConstraint("Root", grp_switch_follow_main)
    cmds.pointConstraint("Root", grp_switch_follow_main)
    cmds.xform(grp_switch_torso, t=(30, 0, 0), r=True)

    # Set visibility state for ik fk ctrls
    nd_ikfk_vis_cond = cmds.createNode('condition', ss=True, n="ikfk_torso_vis_cond")
    cmds.setAttr(nd_ikfk_vis_cond + ".colorIfTrueR", 1)
    cmds.setAttr(nd_ikfk_vis_cond + ".colorIfFalseR", 0)
    cmds.connectAttr(switch_torso_attr, 'ik_spine_controls.visibility')
    cmds.connectAttr(switch_torso_attr, nd_ikfk_vis_cond + '.firstTerm')
    cmds.connectAttr(nd_ikfk_vis_cond + ".outColorR", 'fk_offset_Spine1_M.visibility')

    # Connect both fk ik rigs to def joints through pont/orient constraint workflow

    torso_list = ["Spine1_M", "Spine2_M", "Chest_M"]
    for jnt in torso_list:
        point_constraint = connect_point_constraint(jnt, "fkx_" + jnt, "ikx_" + jnt, switch_torso_attr)
        cmds.parent(point_constraint, "constraints")
        orient_constraint = connect_orient_constraint(jnt, "fkx_" + jnt, "ikx_" + jnt, switch_torso_attr)
        cmds.parent(orient_constraint, "constraints")
