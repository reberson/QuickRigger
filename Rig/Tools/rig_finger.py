import maya.cmds as cmds
from definitions import CONTROLS_DIR
from System.file_handle import file_read_yaml, import_curve

# TODO: Refactor to Class objects


def create_finger_rig(dict):
    sides = ["_R", "_L"]
    for side in sides:
        # Create Finger groups
        finger_grp = cmds.group(em=True, n="fk_offset_fingers{0}".format(side))
        cmds.matchTransform(finger_grp, "Wrist{0}".format(side))
        cmds.parent(finger_grp, "fk_system")
        # List all necessary joints
        finger_list = ["IndexMeta{0}".format(side), "MiddleMeta{0}".format(side), "RingMeta{0}".format(side), "PinkyMeta{0}".format(side), "ThumbFinger1{0}".format(side), "ThumbFinger2{0}".format(side), "ThumbFinger3{0}".format(side), "IndexFinger1{0}".format(side), "IndexFinger2{0}".format(side), "IndexFinger3{0}".format(side), "MiddleFinger1{0}".format(side), "MiddleFinger2{0}".format(side), "MiddleFinger3{0}".format(side), "RingFinger1{0}".format(side), "RingFinger2{0}".format(side), "RingFinger3{0}".format(side),  "PinkyFinger1{0}".format(side),  "PinkyFinger2{0}".format(side),  "PinkyFinger3{0}".format(side)]

        # Create FK rig
        for joint in finger_list:
            if cmds.objExists(joint):
                jd = dict[joint]
                grp_offset = cmds.group(n="fk_offset_" + jd[3], em=True)
                grp_sdk = cmds.group(n="fk_sdk_" + jd[3], em=True)
                grp_sdk_sec = cmds.group(n="fk_sdk_secondary_" + jd[3], em=True)
                grp_flip = cmds.group(n="fk_flip_" + jd[3], em=True)
                if "Meta" in joint:
                    ctrl = cmds.rename(import_curve(file_read_yaml(CONTROLS_DIR + "fk_FingerMeta_R.yaml")), "fk_" + jd[3])
                else:
                    ctrl = cmds.rename(import_curve(file_read_yaml(CONTROLS_DIR + "fk_Finger_R.yaml")), "fk_" + jd[3])
                cmds.setAttr(ctrl + ".overrideEnabled", 1)
                if "_R" in side:
                    cmds.setAttr(ctrl + ".overrideColor", 13)
                else:
                    cmds.setAttr(ctrl + ".overrideColor", 6)
                cmds.setAttr(ctrl + ".v", lock=True, k=False, cb=False)
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
            else:
                print("Warning: skipping " + joint)

        # Parent FK linearly
        for joint in finger_list:
            if cmds.objExists(joint):
                jd = dict[joint]
                # if "Meta_" not in joint or "ThumbFinger1_" not in joint:
                #     cmds.parent("fk_offset_" + jd[3], "fkx_" + jd[4])
                # if "Finger1_" in joint:
                #     cmds.parent("fk_offset_" + jd[3], finger_grp)
                if "Meta_" in joint:
                    cmds.parent("fk_offset_" + jd[3], finger_grp)
                elif "Finger1_" in joint:
                    cmds.parent("fk_offset_" + jd[3], finger_grp)
                else:
                    cmds.parent("fk_offset_" + jd[3], "fkx_" + jd[4])



        cmds.select(d=True)

        # Metacarpal version
        # finger_firsts_list = ["fk_offset_ThumbFinger1{0}".format(side), "fk_offset_IndexMeta{0}".format(side), "fk_offset_MiddleMeta{0}".format(side), "fk_offset_RingMeta{0}".format(side), "fk_offset_PinkyMeta{0}".format(side)]
        # # cmds.parent("fk_offset_ThumbFinger1{0}".format(side), finger_grp)
        # # cmds.parent("fk_offset_IndexMeta{0}".format(side), finger_grp)
        # # cmds.parent("fk_offset_MiddleMeta{0}".format(side), finger_grp)
        # # cmds.parent("fk_offset_RingMeta{0}".format(side), finger_grp)
        # # cmds.parent("fk_offset_PinkyMeta{0}".format(side), finger_grp)
        # for finger_joint in finger_firsts_list:
        #     if cmds.objExists(finger_joint):
        #         if cmds.listRelatives(finger_joint, p=True) != "fk_offset_fingers{0}".format(side):
        #             print(finger_joint)
        #             # cmds.parent(finger_joint, finger_grp)
        #             cmds.parent(finger_joint, "fk_offset_fingers{0}".format(side))
        #     else:
        #         print("Warning: skipping " + finger_joint)

        # Connect both fk ik rigs to def joints through pont/orient constraint workflow
        for jnt in finger_list:
            if cmds.objExists(jnt):
                point_constraint = cmds.pointConstraint("fkx_" + jnt, jnt)
                cmds.parent(point_constraint, "constraints")
                orient_constraint = cmds.orientConstraint("fkx_" + jnt, jnt)
                cmds.parent(orient_constraint, "constraints")
                # scale_constraint = cmds.scaleConstraint("fkx_" + jnt, jnt)
                # cmds.parent(scale_constraint, "constraints")

                # Connect hand scaler attribute to joint scale
                # cmds.connectAttr("ikfk_arm{0}".format(side) + '.handScalex', jnt + ".sx")
                # cmds.connectAttr("ikfk_arm{0}".format(side) + '.handScaley', jnt + ".sy")
                # cmds.connectAttr("ikfk_arm{0}".format(side) + '.handScalez', jnt + ".sz")

        # Constraint finger offset groups to wrist joints
        cmds.pointConstraint("Wrist{0}".format(side), finger_grp)
        cmds.orientConstraint("Wrist{0}".format(side), finger_grp)
        cmds.scaleConstraint("Wrist{0}".format(side), finger_grp)

        # blend_node = (cmds.listConnections("ikfk_arm{0}".format(side) + ".ikSwitch", t="blendColors"))[0]
        # cmds.connectAttr(blend_node + ".output", finger_grp + ".scale")
        # cmds.connectAttr("Wrist{0}".format(side) + ".scale", finger_grp + ".scale")

        # if cmds.objExists("cntrl_scale_Wrist{0}".format(side)):
        #     scl_ctrl = "cntrl_scale_Wrist{0}".format(side)
        #     scale_const = cmds.scaleConstraint(scl_ctrl, finger_grp)
        #     cmds.parent(scale_const, "constraints")


