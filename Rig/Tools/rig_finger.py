import maya.cmds as cmds
from Rig.Tools.reference_tools import joint_dictionary_creator
from System.utils import connect_point_constraint, connect_orient_constraint, mirror_object
from definitions import CONTROLS_DIR
from System.file_handle import file_read_yaml, import_curve

# TODO: Refactor to Class objects

def create_finger_rig(dict):
    # Create Finger groups
    finger_grp_r = cmds.group(em=True, n="fk_offset_fingers_R")
    finger_grp_l = cmds.group(em=True, n="fk_offset_fingers_L")
    cmds.matchTransform(finger_grp_r, "Wrist_R")
    cmds.matchTransform(finger_grp_l, "Wrist_L")
    cmds.parent(finger_grp_r, "fk_system")
    cmds.parent(finger_grp_l, "fk_system")
    # TODO: replace this absurd manual setup to list comprehension
    # List all necessary joints
    finger_list = ["IndexMeta_R", "MiddleMeta_R", "RingMeta_R", "PinkyMeta_R", "IndexMeta_L", "MiddleMeta_L", "RingMeta_L", "PinkyMeta_L", "ThumbFinger1_R", "ThumbFinger2_R", "ThumbFinger3_R", "IndexFinger1_R", "IndexFinger2_R", "IndexFinger3_R", "MiddleFinger1_R", "MiddleFinger2_R", "MiddleFinger3_R", "RingFinger1_R", "RingFinger2_R", "RingFinger3_R",  "PinkyFinger1_R",  "PinkyFinger2_R",  "PinkyFinger3_R","ThumbFinger1_L", "ThumbFinger2_L", "ThumbFinger3_L", "IndexFinger1_L", "IndexFinger2_L", "IndexFinger3_L", "MiddleFinger1_L", "MiddleFinger2_L", "MiddleFinger3_L", "RingFinger1_L", "RingFinger2_L", "RingFinger3_L",  "PinkyFinger1_L",  "PinkyFinger2_L",  "PinkyFinger3_L"]

    # Create FK rig
    for joint in finger_list:
        jd = dict[joint]
        grp_offset = cmds.group(n="fk_offset_" + jd[3], em=True)
        grp_sdk = cmds.group(n="fk_sdk_" + jd[3], em=True)
        grp_sdk_sec = cmds.group(n="fk_sdk_secondary_" + jd[3], em=True)
        grp_flip = cmds.group(n="fk_flip_" + jd[3], em=True)
        # ctrl = cmds.circle(n="fk_" + jd[3], r=2, nr=(0, 1, 0))
        if "Meta" in joint:
            ctrl = cmds.rename(import_curve(file_read_yaml(CONTROLS_DIR + "fk_FingerMeta_R.yaml")), "fk_" + jd[3])
        else:
            ctrl = cmds.rename(import_curve(file_read_yaml(CONTROLS_DIR + "fk_Finger_R.yaml")), "fk_" + jd[3])
        cmds.setAttr(ctrl + ".overrideEnabled", 1)
        cmds.setAttr(ctrl + ".overrideColor", 18)
        cmds.select(d=True)
        jnt = cmds.joint(n="fkx_" + jd[3])
        cmds.setAttr(jnt + ".drawStyle", 2)
        cmds.select(d=True)
        cmds.parent(jnt, ctrl)
        cmds.parent(ctrl, grp_flip)
        cmds.parent(grp_flip, grp_sdk_sec)
        cmds.parent(grp_sdk_sec, grp_sdk)
        cmds.parent(grp_sdk, grp_offset)
        cmds.xform(grp_offset, ws=True, t=jd[0], ro=jd[1], roo=jd[2])

    # Parent FK linearly
    for joint in finger_list:
        jd = dict[joint]
        if "Meta_" not in joint or "ThumbFinger1_" not in joint:
            cmds.parent("fk_offset_" + jd[3], "fkx_" + jd[4])


    cmds.select(d=True)

    # Metacarpal version
    cmds.parent("fk_offset_ThumbFinger1_R", finger_grp_r)
    cmds.parent("fk_offset_IndexMeta_R", finger_grp_r)
    cmds.parent("fk_offset_MiddleMeta_R", finger_grp_r)
    cmds.parent("fk_offset_RingMeta_R", finger_grp_r)
    cmds.parent("fk_offset_PinkyMeta_R", finger_grp_r)

    cmds.parent("fk_offset_ThumbFinger1_L", finger_grp_l)
    cmds.parent("fk_offset_IndexMeta_L", finger_grp_l)
    cmds.parent("fk_offset_MiddleMeta_L", finger_grp_l)
    cmds.parent("fk_offset_RingMeta_L", finger_grp_l)
    cmds.parent("fk_offset_PinkyMeta_L", finger_grp_l)


    # Connect both fk ik rigs to def joints through pont/orient constraint workflow

    for jnt in finger_list:
        point_constraint = cmds.pointConstraint("fkx_" + jnt, jnt)
        cmds.parent(point_constraint, "constraints")
        orient_constraint = cmds.orientConstraint("fkx_" + jnt, jnt)
        cmds.parent(orient_constraint, "constraints")

    # Constraint finger offset groups to wrist joints

    cmds.pointConstraint("Wrist_R", finger_grp_r)
    cmds.orientConstraint("Wrist_R", finger_grp_r)
    cmds.pointConstraint("Wrist_L", finger_grp_l)
    cmds.orientConstraint("Wrist_L", finger_grp_l)




