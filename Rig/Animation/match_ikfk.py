from maya import cmds, OpenMaya

NAMESPACE = ""


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

    def set_fk_to_ik(self, ik_tgt, fk_source, pv_tgt, jnt_chain):
        cmds.matchTransform(ik_tgt, fk_source, scl=False)
        pv_pos = self.calculate_pv_position(jnt_chain, 10)
        cmds.xform(pv_tgt, ws=True, t=pv_pos)
        if "Leg_" in ik_tgt:
            if "_R" in ik_tgt:
                cmds.matchTransform(self.return_lists(NAMESPACE)[0] + "IKToes_R", jnt_chain[3], scl=False)
            else:
                cmds.matchTransform(self.return_lists(NAMESPACE)[0] + "IKToes_L", jnt_chain[3], scl=False)

    def set_ik_to_fk(self, jnt_chain):
        for jnt in jnt_chain:
            rot = cmds.xform(self.return_lists(NAMESPACE)[0] + "IKX" + jnt, q=True, r=True, ro=True)
            cmds.matchTransform(self.return_lists(NAMESPACE)[0] + "FK" + jnt,
                                self.return_lists(NAMESPACE)[0] + "IKX" + jnt,
                                scl=False,
                                rot=True, pos=False)

    # set button functions
    def ik_fk_arm_r(self, *args):
        self.set_ik_to_fk(self.def_joints_arm_R)
        cmds.setAttr(self.return_lists(NAMESPACE)[0] + "FKIKArm_R.FKIKBlend", 0)

    def fk_ik_arm_r(self, *args):
        self.set_fk_to_ik(self.return_lists(NAMESPACE)[0] + "IKArm_R",
                          self.return_lists(NAMESPACE)[0] + "AlignIKToWrist_R",
                          self.return_lists(NAMESPACE)[0] + "PoleArm_R", self.return_lists(NAMESPACE)[1])
        cmds.setAttr(self.return_lists(NAMESPACE)[0] + "FKIKArm_R.FKIKBlend", 10)

    def ik_fk_arm_l(self, *args):
        self.set_ik_to_fk(self.def_joints_arm_L)
        cmds.setAttr(self.return_lists(NAMESPACE)[0] + "FKIKArm_L.FKIKBlend", 0)

    def fk_ik_arm_l(self, *args):
        self.set_fk_to_ik(self.return_lists(NAMESPACE)[0] + "IKArm_L",
                          self.return_lists(NAMESPACE)[0] + "AlignIKToWrist_L",
                          self.return_lists(NAMESPACE)[0] + "PoleArm_L", self.return_lists(NAMESPACE)[2])
        cmds.setAttr(self.return_lists(NAMESPACE)[0] + "FKIKArm_L.FKIKBlend", 10)

    def ik_fk_leg_r(self, *args):
        self.set_ik_to_fk(self.def_joints_leg_R)
        cmds.setAttr(self.return_lists(NAMESPACE)[0] + "FKIKLeg_R.FKIKBlend", 0)

    def fk_ik_leg_r(self, *args):
        self.set_fk_to_ik(self.return_lists(NAMESPACE)[0] + "IKLeg_R",
                          self.return_lists(NAMESPACE)[0] + "AlignIKToAnkle_R",
                          self.return_lists(NAMESPACE)[0] + "PoleLeg_R", self.return_lists(NAMESPACE)[3])
        cmds.setAttr(self.return_lists(NAMESPACE)[0] + "FKIKLeg_R.FKIKBlend", 10)

    def ik_fk_leg_l(self, *args):
        self.set_ik_to_fk(self.def_joints_leg_L)
        cmds.setAttr(self.return_lists(NAMESPACE)[0] + "FKIKLeg_L.FKIKBlend", 0)

    def fk_ik_leg_l(self, *args):
        self.set_fk_to_ik(self.return_lists(NAMESPACE)[0] + "IKLeg_L",
                          self.return_lists(NAMESPACE)[0] + "AlignIKToAnkle_L",
                          self.return_lists(NAMESPACE)[0] + "PoleLeg_L", self.return_lists(NAMESPACE)[4])
        cmds.setAttr(self.return_lists(NAMESPACE)[0] + "FKIKLeg_L.FKIKBlend", 10)

    def create_window(self):
        window_name = "Match IK FK"

        if cmds.window(window_name, exists=True):
            cmds.deleteUI(window_name, window=True)

        window_ikfk = cmds.window(window_name, title=window_name, rtf=True, s=False, tlb=True, mb=True)

        cmds.columnLayout(columnAttach=('both', 5), rowSpacing=10, columnWidth=250, adj=True, mar=15)

        def change_namespace(name_item):
            global NAMESPACE
            NAMESPACE = name_item

        cmds.columnLayout(adj=True)
        cmds.optionMenu(label='Namespace', changeCommand=change_namespace)
        namespaces = cmds.namespaceInfo(lon=True)
        cmds.menuItem(label="")
        for name in namespaces:
            if "UI" not in name and "shared" not in name:
                cmds.menuItem(label=name + ":")

        cmds.setParent('..')

        layout_c = cmds.rowColumnLayout(numberOfColumns=3, columnWidth=[(1, 100), (2, 100), (3, 100)], rs=(10, 10))
        cmds.button(label="IK to FK", command=self.ik_fk_arm_r)
        cmds.text(label="Arm R")
        cmds.button(label="FK to IK", command=self.fk_ik_arm_r)
        cmds.button(label="IK to FK", command=self.ik_fk_arm_l)
        cmds.text(label="Arm L")
        cmds.button(label="FK to IK", command=self.fk_ik_arm_l)
        cmds.button(label="IK to FK", command=self.ik_fk_leg_r)
        cmds.text(label="Leg R")
        cmds.button(label="FK to IK", command=self.fk_ik_leg_r)
        cmds.button(label="IK to FK", command=self.ik_fk_leg_l)
        cmds.text(label="Leg L")
        cmds.button(label="FK to IK", command=self.fk_ik_leg_l)
        cmds.setParent('..')

        cmds.showWindow(window_ikfk)


window = IkFKWindow()
