import maya.cmds as cmds
from scripts.autorigger.rig_tools.layout_tools import joint_dictionary_creator_source
from scripts.autorigger.shared.utils import mirror_joint


def create_rig_structure():
    rig_grp = cmds.group(em=True, n="rig")
    motion_grp = cmds.group(em=True, n="motion_system")
    def_grp = cmds.group(em=True, n="deformation_joints")
    construction_grp = cmds.group(em=True, n="construction_joints")
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
    scale_grp = cmds.group(em=True, n="scale_system")
    grp_follow_main_fkik = cmds.group(em=True, n="follow_ikfk_main")
    grp_follow_root_fkik = cmds.group(em=True, n="follow_ikfk_root")
    geo_grp = cmds.group(em=True, n="geometry")

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
    cmds.parent(scale_grp, motion_grp)
    cmds.parent(construction_grp, rig_grp)
    cmds.parent(geo_grp, rig_grp)
    cmds.parent(def_grp, rig_grp)

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
    cmds.connectAttr(nd_main_scale + '.output', scale_grp + ".scale")

    # Meshes Layer
    # create layer
    layer_meshes = cmds.createDisplayLayer(n="meshes", e=True)
    # unlocked layer = 0, locked = 2
    cmds.setAttr(layer_meshes + ".displayType", 2)
    # visible layer
    cmds.setAttr(layer_meshes + ".visibility", 1)
    # disable color override
    cmds.setAttr(layer_meshes + ".color", 0)
    # add objects to layer
    objects_to_move = cmds.ls("geometry")
    cmds.editDisplayLayerMembers(layer_meshes, objects_to_move, nr=False)

    # Deformation joints layer
    layer_deformation = cmds.createDisplayLayer(n="deformation", e=True)
    cmds.setAttr(layer_deformation + ".displayType", 2)
    cmds.setAttr(layer_deformation + ".visibility", 0)
    cmds.setAttr(layer_deformation + ".color", 0)
    objects_to_move = cmds.ls("deformation_joints")
    cmds.editDisplayLayerMembers(layer_deformation, objects_to_move, nr=False)

    # Primary controls layer - Will move the objects later, just the actual controls (inside each module)
    layer_ctrls_primary = cmds.createDisplayLayer(n="body_primary", e=True)
    cmds.setAttr(layer_ctrls_primary + ".displayType", 0)
    cmds.setAttr(layer_ctrls_primary + ".visibility", 1)
    cmds.setAttr(layer_ctrls_primary + ".color", 0)

    # Secondary controls layer - Will move the objects later, just the actual controls (inside each module)
    layer_ctrls_secondary = cmds.createDisplayLayer(n="body_secondary", e=True)
    cmds.setAttr(layer_ctrls_secondary + ".displayType", 0)
    cmds.setAttr(layer_ctrls_secondary + ".visibility", 1)
    cmds.setAttr(layer_ctrls_secondary + ".color", 0)

    # Tweak controls layer - Will move the objects later, just the actual controls (inside each module)
    layer_ctrls_tweak = cmds.createDisplayLayer(n="body_tweaks", e=True)
    cmds.setAttr(layer_ctrls_secondary + ".displayType", 0)
    cmds.setAttr(layer_ctrls_secondary + ".visibility", 1)
    cmds.setAttr(layer_ctrls_secondary + ".color", 0)

    # Stretch/Squash controls layer - Will move the objects later, just the actual controls (inside each module)
    layer_ctrls_stretch = cmds.createDisplayLayer(n="body_stretch", e=True)
    cmds.setAttr(layer_ctrls_secondary + ".displayType", 0)
    cmds.setAttr(layer_ctrls_secondary + ".visibility", 1)
    cmds.setAttr(layer_ctrls_secondary + ".color", 0)


def create_deform_rig():
    """Completes the existing reference rig to become a complete deformation joint"""
    joint_data = joint_dictionary_creator_source("Root")

    cmds.parent("Root", "deformation_joints")

    for key in joint_data:
        # if "scapula_r" or "hip_r" or "eye_r" or "scapula_l" or "hip_l" or "eye_l" == str(key).lower():
        #     mirror_joint(str(key))
        if "scapula_r" == str(key).lower() or "scapula_l" == str(key).lower():
            mirror_joint(str(key))
        elif "hip_r" == str(key).lower() or "hip_l" == str(key).lower():
            mirror_joint(str(key))
        elif "wing_scapula_r" == str(key).lower() or "wing_scapula_l" == str(key).lower():
            mirror_joint(str(key))

    # Freeze Transforms
    all_jnts = cmds.ls(type="joint")
    for joint in all_jnts:
        cmds.makeIdentity(joint, a=True, r=True)

    # Create Twist joints
    # sides = ["_R", "_L"]
    # for side in sides:
    #     twist_shoulder = create_twist_joint("Shoulder{0}".format(side), "Elbow{0}".format(side), "Shoulder_Twist{0}".format(side))
    #     cmds.parent(twist_shoulder[1], "constraints")
    #     twist_elbow = create_twist_joint("Elbow{0}".format(side), "Wrist{0}".format(side), "Elbow_Twist{0}".format(side))
    #     cmds.parent(twist_elbow[1], "constraints")
    #     twist_hip = create_twist_joint("Hip{0}".format(side), "Knee{0}".format(side), "Hip_Twist{0}".format(side))
    #     cmds.parent(twist_hip[1], "constraints")
    #     twist_knee = create_twist_joint("Knee{0}".format(side), "Ankle{0}".format(side), "Knee_Twist{0}".format(side))
    #     cmds.parent(twist_knee[1], "constraints")
    # twist_neck = create_twist_joint("Neck_M", "Head_M", "Neck_Twist")
    # cmds.parent(twist_neck[1], "constraints")


def create_rig_structure_face():

    if cmds.objExists("rig"):
        grp_rig = "rig"
    else:
        grp_rig = cmds.group(em=True, n="rig")

    grp_sys = cmds.group(em=True, n="face_system")
    grp_origin = cmds.group(em=True, n="face_origin")
    cmds.setAttr(grp_origin + ".visibility", 0)
    grp_follow_head = cmds.group(em=True, n="face_constrain_head")
    grp_follow_jaw = cmds.group(em=True, n="face_constrain_jaw")
    loc_jaw = cmds.spaceLocator(n="loc_jaw")
    cmds.setAttr(loc_jaw[0] + ".visibility", 0)


    if cmds.objExists("deformation_joints"):
        def_grp = "deformation_joints"
    else:
        def_grp = cmds.group(em=True, n="deformation_joints")
        cmds.parent(def_grp, grp_rig)
    grp_mediators = cmds.group(em=True, n="face_mediators")
    grp_const = cmds.group(em=True, n="face_constraints")
    cmds.parent(grp_origin, grp_sys)
    cmds.parent(grp_follow_head, grp_sys)
    cmds.parent(grp_follow_jaw, grp_follow_head)
    cmds.parent(loc_jaw[0], grp_follow_jaw)
    cmds.parent(grp_mediators, grp_sys)
    cmds.parent(grp_const, grp_sys)
    cmds.parent(grp_sys, grp_rig)

    cmds.pointConstraint("Facial", grp_follow_head)
    cmds.orientConstraint("Facial", grp_follow_head)

    if not cmds.objExists("Head_M"):
        cmds.parent("Facial", def_grp)
    else:
        cmds.scaleConstraint("fkx_Head_M", grp_follow_head)
    # Create Projection system groups
    grp_proj_sys = cmds.group(em=True, n="face_projection_system")
    cmds.setAttr(grp_proj_sys + ".visibility", 0)
    grp_proj_fol = cmds.group(em=True, n="face_projection_follicles")
    grp_proj_rib = cmds.group(em=True, n="face_ribbons")
    cmds.parent(grp_proj_rib, grp_origin)
    cmds.parent(grp_proj_fol, grp_origin)
    cmds.matchTransform(grp_proj_sys, grp_follow_head)
    cmds.parent(grp_proj_sys, grp_follow_head)

    # Face Control Layer - Will move objects after inside each module
    # create layer
    layer_ctrls_face_primary = cmds.createDisplayLayer(n="face_primary", e=True)
    layer_ctrls_face_secondary = cmds.createDisplayLayer(n="face_secondary", e=True)
    # unlocked layer = 0, locked = 2
    cmds.setAttr(layer_ctrls_face_primary + ".displayType", 0)
    cmds.setAttr(layer_ctrls_face_secondary + ".displayType", 0)
    # visible layer
    cmds.setAttr(layer_ctrls_face_primary + ".visibility", 1)
    cmds.setAttr(layer_ctrls_face_secondary + ".visibility", 1)
    cmds.setAttr(layer_ctrls_face_primary + ".color", 0)
    cmds.setAttr(layer_ctrls_face_secondary + ".color", 0)


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


def set_scale_compensate(attr_value=0):
    jnt_list = cmds.listRelatives("Root", type="joint", ad=True)
    for jnt in jnt_list:
        cmds.setAttr(jnt + ".segmentScaleCompensate", attr_value)
    cmds.setAttr("Root.segmentScaleCompensate", attr_value)
