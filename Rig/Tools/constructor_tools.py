import maya.cmds as cmds
from Rig.Tools.reference_tools import joint_dictionary_creator


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


def create_deform_rig():
    """Completes the existing reference rig to become a complete deformation joint"""
    create_rig_structure()
    joint_data = joint_dictionary_creator()
    cmds.rename("joint_reference", "deformation_joints")
    cmds.parent("deformation_joints", "rig")
    geo_grp = cmds.group(em=True, n="geometry")
    cmds.parent(geo_grp, "rig")

    for key in joint_data:
        # if "scapula_r" or "hip_r" or "eye_r" or "scapula_l" or "hip_l" or "eye_l" == str(key).lower():
        #     mirror_joint(str(key))
        if "scapula_r" == str(key).lower() or "scapula_l" == str(key).lower():
            mirror_joint(str(key))
        elif "hip_r" == str(key).lower() or "hip_l" == str(key).lower():
            mirror_joint(str(key))
        elif "eye_r" == str(key).lower() or "eye_l" == str(key).lower():
            mirror_joint(str(key))

    all_jnts = cmds.ls(type="joint")
    for joint in all_jnts:
        cmds.makeIdentity(joint, a=True, r=True)

# TODO: Create a twist joint function by grabbing the half lenght of the joint to the next one and place it in midway


def create_rig_structure():
    rig_grp = cmds.group(em=True, n="rig")
    motion_grp = cmds.group(em=True, n="motion_system")
    main_grp = cmds.group(em=True, n="main_system")
    main_ctrl = cmds.circle(n="Main", r=50, nr=(0, 1, 0))
    root_grp = cmds.group(em=True, n="root_system")
    glob_grp = cmds.group(em=True, n="global_system")
    glob_main_grp = cmds.group(em=True, n="global_constraint_main")
    fk_grp = cmds.group(em=True, n="fk_system")
    ik_grp = cmds.group(em=True, n="ik_system")
    const_grp = cmds.group(em=True, n="constraints")
    driver_grp = cmds.group(em=True, n="drivers_system")
    fkik_grp = cmds.group(em=True, n="fkik_system")
    grp_follow_main_fkik = cmds.group(em=True, n="follow_ikfk_main")
    grp_follow_root_fkik = cmds.group(em=True, n="follow_ikfk_root")
    cmds.parent(grp_follow_main_fkik, fkik_grp)
    cmds.parent(grp_follow_root_fkik, fkik_grp)

    cmds.parent(motion_grp, rig_grp)
    cmds.parent(main_grp, motion_grp)
    cmds.parent(main_ctrl[0], main_grp)
    cmds.parent(glob_grp, motion_grp)
    cmds.parent(glob_main_grp, glob_grp)
    cmds.parent(fk_grp, motion_grp)
    cmds.parent(ik_grp, motion_grp)
    cmds.parent(const_grp, motion_grp)
    cmds.parent(driver_grp, motion_grp)
    cmds.parent(fkik_grp, motion_grp)
    cmds.parent(root_grp, motion_grp)

    cmds.pointConstraint(main_ctrl, glob_main_grp)
    cmds.orientConstraint(main_ctrl, glob_main_grp)
    cmds.orientConstraint(main_ctrl, grp_follow_main_fkik)
    cmds.pointConstraint(main_ctrl, grp_follow_main_fkik)
    cmds.orientConstraint("Root", grp_follow_root_fkik)
    cmds.pointConstraint("Root", grp_follow_root_fkik)

    # Connect Scale from main control to the groups
    nd_main_scale = cmds.createNode('multiplyDivide', ss=True, n='main_scale_multi')
    cmds.connectAttr(main_ctrl[0] + ".scale", nd_main_scale + '.input1')
    cmds.connectAttr(nd_main_scale + '.output', glob_grp + ".scale")
    cmds.connectAttr(nd_main_scale + '.output', main_grp + ".scale")
    cmds.connectAttr(nd_main_scale + '.output', root_grp + ".scale")
    cmds.connectAttr(nd_main_scale + '.output', fk_grp + ".scale")
    cmds.connectAttr(nd_main_scale + '.output', ik_grp + ".scale")
    cmds.connectAttr(nd_main_scale + '.output', driver_grp + ".scale")
    cmds.connectAttr(nd_main_scale + '.output', fkik_grp + ".scale")
    cmds.connectAttr(nd_main_scale + '.output', "joint_reference.scale")

