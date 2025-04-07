import maya.cmds as cmds
from Rig.Tools.layout_tools import joint_dictionary_creator, joint_dictionary_creator_source
import System.file_handle
from System.utils import create_twist_joint, mirror_joint

# TODO: Make possible to build body rig AFTER face rig being built. (low priority)
# TODO: Create a finalization pass where we can clean unused joints
def create_rig_structure():
    rig_grp = cmds.group(em=True, n="rig")
    motion_grp = cmds.group(em=True, n="motion_system")
    def_grp = cmds.group(em=True, n="deformation_joints")
    main_grp = cmds.group(em=True, n="main_system")
    main_ctrl = cmds.circle(n="Main", r=50, nr=(0, 1, 0))
    cmds.setAttr(main_ctrl[0] + ".overrideEnabled", 1)
    cmds.setAttr(main_ctrl[0] + ".overrideColor", 7)
    root_grp = cmds.group(em=True, n="root_system")
    glob_grp = cmds.group(em=True, n="global_system")
    glob_main_grp = cmds.group(em=True, n="global_constraint_main")
    fk_grp = cmds.group(em=True, n="fk_system")
    ik_grp = cmds.group(em=True, n="ik_system")
    const_grp = cmds.group(em=True, n="constraints")
    driver_grp = cmds.group(em=True, n="drivers_system")
    fkik_grp = cmds.group(em=True, n="fkik_system")
    stretch_grp = cmds.group(em=True, n="stretch_system")
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
    cmds.parent(stretch_grp, motion_grp)

    cmds.pointConstraint(main_ctrl, glob_main_grp)
    cmds.orientConstraint(main_ctrl, glob_main_grp)
    cmds.orientConstraint(main_ctrl, grp_follow_main_fkik)
    cmds.pointConstraint(main_ctrl, grp_follow_main_fkik)

    # Connect Scale from main control to the groups
    nd_main_scale = cmds.createNode('multiplyDivide', ss=True, n='main_scale_multi')
    cmds.connectAttr(main_ctrl[0] + ".scale", nd_main_scale + '.input1')
    cmds.connectAttr(nd_main_scale + '.output', glob_grp + ".scale")
    # cmds.connectAttr(nd_main_scale + '.output', main_grp + ".scale")
    cmds.connectAttr(nd_main_scale + '.output', root_grp + ".scale")
    cmds.connectAttr(nd_main_scale + '.output', fk_grp + ".scale")
    cmds.connectAttr(nd_main_scale + '.output', ik_grp + ".scale")
    cmds.connectAttr(nd_main_scale + '.output', driver_grp + ".scale")
    cmds.connectAttr(nd_main_scale + '.output', fkik_grp + ".scale")
    # cmds.connectAttr(nd_main_scale + '.output', "joint_reference.scale")
    cmds.connectAttr(nd_main_scale + '.output', def_grp + ".scale")
    cmds.connectAttr(nd_main_scale + '.output', stretch_grp + ".scale")


def create_deform_rig():
    """Completes the existing reference rig to become a complete deformation joint"""
    joint_data = joint_dictionary_creator_source("Root")

    cmds.parent("deformation_joints", "rig")
    cmds.parent("Root", "deformation_joints")
    geo_grp = cmds.group(em=True, n="geometry")
    cmds.parent(geo_grp, "rig")

    for key in joint_data:
        # if "scapula_r" or "hip_r" or "eye_r" or "scapula_l" or "hip_l" or "eye_l" == str(key).lower():
        #     mirror_joint(str(key))
        if "scapula_r" == str(key).lower() or "scapula_l" == str(key).lower():
            mirror_joint(str(key))
        elif "hip_r" == str(key).lower() or "hip_l" == str(key).lower():
            mirror_joint(str(key))

    # Freeze Transforms
    all_jnts = cmds.ls(type="joint")
    for joint in all_jnts:
        cmds.makeIdentity(joint, a=True, r=True)

    # Create Twist joints
    sides = ["_R", "_L"]
    for side in sides:
        twist_shoulder = create_twist_joint("Shoulder{0}".format(side), "Elbow{0}".format(side), "Shoulder_Twist{0}".format(side))
        cmds.parent(twist_shoulder[1], "constraints")
        twist_elbow = create_twist_joint("Elbow{0}".format(side), "Wrist{0}".format(side), "Elbow_Twist{0}".format(side))
        cmds.parent(twist_elbow[1], "constraints")
        twist_hip = create_twist_joint("Hip{0}".format(side), "Knee{0}".format(side), "Hip_Twist{0}".format(side))
        cmds.parent(twist_hip[1], "constraints")
        twist_knee = create_twist_joint("Knee{0}".format(side), "Ankle{0}".format(side), "Knee_Twist{0}".format(side))
        cmds.parent(twist_knee[1], "constraints")
    twist_neck = create_twist_joint("Neck_M", "Head_M", "Neck_Twist")
    cmds.parent(twist_neck[1], "constraints")


def create_rig_structure_face():

    if cmds.objExists("rig"):
        grp_rig = "rig"
    else:
        grp_rig = cmds.group(em=True, n="rig")

    grp_sys = cmds.group(em=True, n="face_system")
    grp_follow_root = cmds.group(em=True, n="face_constrain_root")
    grp_follow_head = cmds.group(em=True, n="face_constrain_head")

    if cmds.objExists("deformation_joints"):
        def_grp = "deformation_joints"
    else:
        def_grp = cmds.group(em=True, n="deformation_joints")
        cmds.parent(def_grp, grp_rig)
    grp_mediators = cmds.group(em=True, n="face_mediators")
    grp_const = cmds.group(em=True, n="face_constraints")
    cmds.parent(grp_follow_root, grp_sys)
    cmds.parent(grp_follow_head, grp_sys)
    cmds.parent(grp_mediators, grp_sys)
    cmds.parent(grp_const, grp_sys)
    cmds.parent(grp_sys, grp_rig)

    #Checks if there is an existing body rig
    if cmds.objExists("Head_M"):
        cmds.pointConstraint("Head_M", grp_follow_head)
        cmds.orientConstraint("Head_M", grp_follow_head)
    else:
        cmds.parent("Facial", def_grp)


def create_deform_rig_face():
    """Completes the existing reference rig to become a complete deformation joint"""

    joint_data = joint_dictionary_creator_source("Facial")

    for key in joint_data:
        if "eye" in str(key).lower() and "end" not in str(key).lower():
            if "_r" in str(key).lower() or "_l" in str(key).lower():
                mirror_joint(str(key))
        elif "brow" in str(key).lower():
            if "_r" in str(key).lower() or "_l" in str(key).lower():
                mirror_joint(str(key))
        elif "nasolabial" in str(key).lower():
            if "_r" in str(key).lower() or "_l" in str(key).lower():
                mirror_joint(str(key))
        elif "lip" in str(key).lower():
            if "_r" in str(key).lower() or "_l" in str(key).lower():
                mirror_joint(str(key))
        elif "mouth" in str(key).lower():
            if "_r" in str(key).lower() or "_l" in str(key).lower():
                mirror_joint(str(key))
        elif "nostril" in str(key).lower():
            if "_r" in str(key).lower() or "_l" in str(key).lower():
                mirror_joint(str(key))
        elif "eyelid" in str(key).lower():
            if "_r" in str(key).lower() or "_l" in str(key).lower():
                mirror_joint(str(key))
        elif "cheek" in str(key).lower():
            if "_r" in str(key).lower() or "_l" in str(key).lower():
                mirror_joint(str(key))
    # Freeze Transforms
    all_jnts = cmds.listRelatives("Facial", ad=True, type="joint")
    for joint in all_jnts:
        cmds.makeIdentity(joint, a=True, r=True)