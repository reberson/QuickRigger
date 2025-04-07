import maya.cmds as cmds


def create_nose(dict):
    grp_ctrl = cmds.group(em=True, n="nose_control_group")
    cmds.matchTransform(grp_ctrl, "Nose")
    cmds.parent(grp_ctrl, "face_constrain_head")
    jnt_list = cmds.listRelatives("Nose")

    # create base controls
    for jnt in jnt_list:
        jd = dict[jnt]
        grp_offset = cmds.group(em=True, n="offset_" + jnt)
        grp_flip = cmds.group(em=True, n="flip_" + jnt)
        grp_sdk = cmds.group(em=True, n="sdk_" + jnt)
        if "_r" in jnt.lower():
            ctrl = cmds.circle(n="ctrl_" + jnt, cy=1, r=0.75, nr=(0, 1, 0))
            cmds.setAttr(ctrl[0] + ".overrideEnabled", 1)
            cmds.setAttr(ctrl[0] + ".overrideColor", 31)
        elif "_l" in jnt.lower():
            ctrl = cmds.circle(n="ctrl_" + jnt, cy=-1, r=0.75, nr=(0, 1, 0))
            cmds.setAttr(ctrl[0] + ".overrideEnabled", 1)
            cmds.setAttr(ctrl[0] + ".overrideColor", 18)
        else:
            ctrl = cmds.circle(n="ctrl_" + jnt, cy=1, r=0.75, nr=(0, 1, 0))
            cmds.setAttr(ctrl[0] + ".overrideEnabled", 1)
            cmds.setAttr(ctrl[0] + ".overrideColor", 21)

        cmds.select(d=True)
        xjnt = cmds.joint(n="x_" + jnt)
        cmds.setAttr(xjnt + ".radius", 0.5)
        cmds.select(d=True)
        cmds.setAttr(xjnt + ".drawStyle", 2)

        cmds.parent(xjnt, ctrl[0])
        cmds.parent(ctrl[0], grp_flip)
        cmds.parent(grp_flip, grp_sdk)
        cmds.parent(grp_sdk, grp_offset)
        cmds.parent(grp_offset, grp_ctrl)
        cmds.xform(grp_offset, ws=True, t=jd[0], ro=jd[1], roo=jd[2])
        if "_L" in jnt:
            cmds.xform(grp_flip, r=True, ro=(0, 180, 0))


    # Create general Nose ctrl
    nose_grp = cmds.group(em=True, n="offset_NoseMain")
    nose_flip = cmds.group(em=True, n="flip_NoseMain")
    nose_sdk = cmds.group(em=True, n="sdk_NoseMain")
    nose_ctrl = cmds.circle(n="ctrl_NoseMain", cy=1, r=1.5, nr=(0, 1, 0))
    cmds.setAttr(nose_ctrl[0] + ".overrideEnabled", 1)
    cmds.setAttr(nose_ctrl[0] + ".overrideColor", 17)
    cmds.parent(nose_ctrl[0], nose_flip)
    cmds.parent(nose_flip, nose_sdk)
    cmds.parent(nose_sdk, nose_grp)
    cmds.parent(nose_grp, grp_ctrl)
    cmds.matchTransform(nose_grp, "NoseTip_M")

    # parent Nose separate controls to nose main group
    for jnt in jnt_list:
        cmds.parent("offset_" + jnt, "ctrl_NoseMain")

    # attach def joints to ctrl jnts
    for jnt in jnt_list:
        cmds.parent(cmds.pointConstraint("x_" + jnt, jnt), "face_constraints")
        cmds.parent(cmds.orientConstraint("x_" + jnt, jnt), "face_constraints")



