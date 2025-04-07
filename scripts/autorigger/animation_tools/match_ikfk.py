from maya import cmds, OpenMaya

NAMESPACE = ""
MULTIFRAME = False
STARTFRAME = 0
ENDFRAME = 60


class IkFKWindow:
    def __init__(self):
        self.create_window()
        self.def_joints_arm_R = ["Shoulder_R", "Elbow_R", "Wrist_R"]
        self.def_joints_arm_L = ["Shoulder_L", "Elbow_L", "Wrist_L"]
        self.def_joints_leg_R = ["Hip_R", "Knee_R", "Ankle_R", "Toes_R"]
        self.def_joints_leg_L = ["Hip_L", "Knee_L", "Ankle_L", "Toes_R"]

    def set_namespace(self, name=None):
        if name is None:
            name = ""
        return name

    def return_lists(self, new_name):
        nspace = self.set_namespace(name=new_name)
        fk_arm_R = [nspace + "FKShoulder_R", nspace + "FKElbow_R", nspace + "FKWrist_R"]
        fk_arm_L = [nspace + "FKShoulder_L", nspace + "FKElbow_L", nspace + "FKWrist_L"]
        fk_leg_R = [nspace + "FKHip_R", nspace + "FKKnee_R", nspace + "FKAnkle_R", nspace + "FKToes_R"]
        fk_leg_L = [nspace + "FKHip_L", nspace + "FKKnee_L", nspace + "FKAnkle_L", nspace + "FKToes_L"]
        return nspace, fk_arm_R, fk_arm_L, fk_leg_R, fk_leg_L

    def calculate_pv_position(self, jnts, distance):
        start = cmds.xform(jnts[0], q=True, ws=True, t=True)
        mid = cmds.xform(jnts[1], q=True, ws=True, t=True)
        end = cmds.xform(jnts[2], q=True, ws=True, t=True)
        startV = OpenMaya.MVector(start[0], start[1], start[2])
        midV = OpenMaya.MVector(mid[0], mid[1], mid[2])
        endV = OpenMaya.MVector(end[0], end[1], end[2])
        startEnd = endV - startV
        startMid = (midV - startV) * distance
        dotP = startMid * startEnd
        proj = float(dotP) / float(startEnd.length())
        startEndN = startEnd.normal()
        projV = startEndN * proj
        arrowV = startMid - projV
        arrowV *= 0.5
        finalV = arrowV + midV
        return ([finalV.x, finalV.y, finalV.z])

    def list_keyframes(self, key_items):
        keyframe_list = []
        for keyed_joint in key_items:
            keys = cmds.keyframe(keyed_joint, q=True)
            if keys:
                for key in keys:
                    keyframe_list.append(int(key))
        return keyframe_list

    def set_fk_to_ik(self, ik_tgt, fk_source, pv_tgt, jnt_chain, limb):
        global MULTIFRAME
        global STARTFRAME
        global ENDFRAME
        if not MULTIFRAME:
            cmds.matchTransform(ik_tgt, fk_source, scl=False)
            pv_pos = self.calculate_pv_position(jnt_chain, 10)
            cmds.xform(pv_tgt, ws=True, t=pv_pos)
            if "Leg_" in ik_tgt:
                cmds.matchTransform(self.return_lists(NAMESPACE)[0] + "IKToes_" + limb.split("_")[1], jnt_chain[3],
                                    scl=False)
                cmds.setKeyframe(self.return_lists(NAMESPACE)[0] + "IKToes_" + limb.split("_")[1])
            cmds.setKeyframe(ik_tgt)
            cmds.setAttr(self.return_lists(NAMESPACE)[0] + "FKIK{0}.FKIKBlend".format(limb), 10)
            cmds.setKeyframe(self.return_lists(NAMESPACE)[0] + "FKIK{0}.FKIKBlend".format(limb))
            cmds.setKeyframe(self.return_lists(NAMESPACE)[0] + "Pole{0}".format(limb))
        else:
            fk_ctrls = []
            for jnt in jnt_chain:
                fk_ctrls.append("FK" + jnt)
            key_list = self.list_keyframes(jnt_chain)
            for frame in range(STARTFRAME, ENDFRAME + 1):
                current_frame = cmds.currentTime(frame, edit=True)
                if current_frame in key_list:
                    cmds.matchTransform(ik_tgt, fk_source, scl=False)
                    pv_pos = self.calculate_pv_position(jnt_chain, 10)
                    cmds.xform(pv_tgt, ws=True, t=pv_pos)
                    if "Leg_" in ik_tgt:
                        cmds.matchTransform(self.return_lists(NAMESPACE)[0] + "IKToes_" + limb.split("_")[1],
                                            jnt_chain[3], scl=False)
                        cmds.setKeyframe(self.return_lists(NAMESPACE)[0] + "IKToes_" + limb.split("_")[1])
                    cmds.setKeyframe(ik_tgt)
                    cmds.setAttr(self.return_lists(NAMESPACE)[0] + "FKIK{0}.FKIKBlend".format(limb), 10)
                    cmds.setKeyframe(self.return_lists(NAMESPACE)[0] + "FKIK{0}.FKIKBlend".format(limb))
                    cmds.setKeyframe(self.return_lists(NAMESPACE)[0] + "Pole{0}".format(limb))

    def set_ik_to_fk(self, jnt_chain, limb):
        global MULTIFRAME
        global STARTFRAME
        global ENDFRAME
        if not MULTIFRAME:
            for jnt in jnt_chain:
                rot = cmds.xform(self.return_lists(NAMESPACE)[0] + "IKX" + jnt, q=True, r=True, ro=True)

                cmds.matchTransform(self.return_lists(NAMESPACE)[0] + "FK" + jnt,
                                    self.return_lists(NAMESPACE)[0] + "IKX" + jnt,
                                    scl=False,
                                    rot=True, pos=False)
                cmds.xform(self.return_lists(NAMESPACE)[0] + "FK" + jnt, t=(0, 0, 0))
                cmds.setKeyframe(self.return_lists(NAMESPACE)[0] + "FK" + jnt)
            cmds.setAttr(self.return_lists(NAMESPACE)[0] + "FKIK{0}.FKIKBlend".format(limb), 0)
            cmds.setKeyframe(self.return_lists(NAMESPACE)[0] + "FKIK{0}.FKIKBlend".format(limb))
        else:
            ik_ctrls = [self.return_lists(NAMESPACE)[0] + "IK{0}".format(limb),
                        self.return_lists(NAMESPACE)[0] + "Pole{0}".format(limb)]
            key_list = self.list_keyframes(ik_ctrls)

            for frame in range(STARTFRAME, ENDFRAME + 1):
                current_frame = cmds.currentTime(frame, edit=True)
                if current_frame in key_list:
                    cmds.setAttr(self.return_lists(NAMESPACE)[0] + "FKIK{0}.FKIKBlend".format(limb), 0)
                    cmds.setKeyframe(self.return_lists(NAMESPACE)[0] + "FKIK{0}.FKIKBlend".format(limb))
                    for jnt in jnt_chain:
                        rot = cmds.xform(self.return_lists(NAMESPACE)[0] + "IKX" + jnt, q=True, r=True, ro=True)

                        cmds.matchTransform(self.return_lists(NAMESPACE)[0] + "FK" + jnt,
                                            self.return_lists(NAMESPACE)[0] + "IKX" + jnt,
                                            scl=False,
                                            rot=True, pos=False)
                        cmds.xform(self.return_lists(NAMESPACE)[0] + "FK" + jnt, t=(0, 0, 0))
                        cmds.setKeyframe(self.return_lists(NAMESPACE)[0] + "FK" + jnt)

    def create_window(self):
        window_name = "Match IK FK"

        if cmds.window(window_name, exists=True):
            cmds.deleteUI(window_name, window=True)

        window_ikfk = cmds.window(window_name, title=window_name, rtf=True, s=False, tlb=True, mb=True)

        cmds.columnLayout(columnAttach=('both', 5), rowSpacing=10, columnWidth=250, adj=True, mar=15)

        def change_namespace(name_item):
            global NAMESPACE
            NAMESPACE = name_item

        def refresh_namespace(option_menu):
            for item in cmds.optionMenu(option_menu, q=True, ill=True) or []:
                cmds.deleteUI(item)
            names = cmds.namespaceInfo(lon=True)
            cmds.menuItem(label="", parent=option_menu)
            for new_item in names:
                if "UI" not in new_item and "shared" not in new_item:
                    cmds.menuItem(label=new_item + ":", parent=option_menu)

        def set_single(self):
            global MULTIFRAME
            MULTIFRAME = False
            cmds.floatField(sframe, e=True, en=False)
            cmds.floatField(eframe, e=True, en=False)

        def set_multi(self):
            global MULTIFRAME
            MULTIFRAME = True
            cmds.floatField(sframe, e=True, en=True)
            cmds.floatField(eframe, e=True, en=True)

        def set_start_frame(value):
            global STARTFRAME
            STARTFRAME = int(value)

        def set_end_frame(value):
            global ENDFRAME
            ENDFRAME = int(value)

        cmds.rowColumnLayout(adj=1, nc=3, rs=(10, 10))
        op = cmds.optionMenu(label='Namespace', changeCommand=change_namespace)
        namespaces = cmds.namespaceInfo(lon=True)
        cmds.menuItem(label="")
        for name in namespaces:
            if "UI" not in name and "shared" not in name:
                cmds.menuItem(label=name + ":")
        cmds.separator(w=5, vis=False)
        cmds.iconTextButton(style='iconOnly', image1='refresh.png', label='refresh', command=lambda *args: refresh_namespace(op))
        cmds.setParent('..')

        layout_c = cmds.rowColumnLayout(numberOfColumns=3, columnWidth=[(1, 100), (2, 100), (3, 100)], rs=(10, 10))
        cmds.button(label="IK to FK", command=lambda *args: self.set_ik_to_fk(self.def_joints_arm_R, "Arm_R"))
        cmds.text(label="Arm R")
        cmds.button(label="FK to IK",
                    command=lambda *args: self.set_fk_to_ik(self.return_lists(NAMESPACE)[0] + "IKArm_R",
                                                            self.return_lists(NAMESPACE)[0] + "AlignIKToWrist_R",
                                                            self.return_lists(NAMESPACE)[0] + "PoleArm_R",
                                                            self.return_lists(NAMESPACE)[1], "Arm_R"))

        cmds.button(label="IK to FK", command=lambda *args: self.set_ik_to_fk(self.def_joints_arm_L, "Arm_L"))
        cmds.text(label="Arm L")
        cmds.button(label="FK to IK",
                    command=lambda *args: self.set_fk_to_ik(self.return_lists(NAMESPACE)[0] + "IKArm_L",
                                                            self.return_lists(NAMESPACE)[0] + "AlignIKToWrist_L",
                                                            self.return_lists(NAMESPACE)[0] + "PoleArm_L",
                                                            self.return_lists(NAMESPACE)[2], "Arm_L"))

        cmds.button(label="IK to FK", command=lambda *args: self.set_ik_to_fk(self.def_joints_leg_R, "Leg_R"))
        cmds.text(label="Leg R")
        cmds.button(label="FK to IK",
                    command=lambda *args: self.set_fk_to_ik(self.return_lists(NAMESPACE)[0] + "IKLeg_R",
                                                            self.return_lists(NAMESPACE)[0] + "AlignIKToAnkle_R",
                                                            self.return_lists(NAMESPACE)[0] + "PoleLeg_R",
                                                            self.return_lists(NAMESPACE)[3], "Leg_R"))

        cmds.button(label="IK to FK", command=lambda *args: self.set_ik_to_fk(self.def_joints_leg_L, "Leg_L"))
        cmds.text(label="Leg L")
        cmds.button(label="FK to IK",
                    command=lambda *args: self.set_fk_to_ik(self.return_lists(NAMESPACE)[0] + "IKLeg_L",
                                                            self.return_lists(NAMESPACE)[0] + "AlignIKToAnkle_L",
                                                            self.return_lists(NAMESPACE)[0] + "PoleLeg_L",
                                                            self.return_lists(NAMESPACE)[4], "Leg_L"))
        cmds.setParent('..')

        cmds.columnLayout()
        cmds.radioButtonGrp(labelArray2=['Single Frame', 'Timeline Range'], numberOfRadioButtons=2, on1=set_single,
                            on2=set_multi, sl=1)
        cmds.setParent('..')

        layout_c = cmds.rowColumnLayout(numberOfColumns=4, columnWidth=[(1, 75), (2, 50), (3, 75), (4, 50)],
                                        rs=(10, 10))
        cmds.text(label="Start frame:")
        sframe = cmds.floatField(en=False, pre=1, cc=set_start_frame)
        cmds.text(label="End frame:")
        eframe = cmds.floatField(en=False, pre=1, cc=set_end_frame)
        cmds.setParent('..')

        cmds.showWindow(window_ikfk)
