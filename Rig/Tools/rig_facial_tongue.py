import maya.cmds as cmds


def create_tongue(dict):
    grp_ctrl = cmds.group(em=True, n="tongue_control_group")
    cmds.matchTransform(grp_ctrl, "Facial")
    cmds.parent(grp_ctrl, "face_constrain_head")
    jnt_list_all = cmds.listRelatives("Facial", ad=True)
    jnt_list=[]

    for jnt in jnt_list_all:
        if "tongue" in jnt.lower():
            jnt_list.append(jnt)
            if "_end" in jnt.lower():
                jnt_list.remove(jnt)
    jnt_list.sort()

    # create base fk controls
    for jnt in jnt_list:
        jd = dict[jnt]
        grp_offset = cmds.group(em=True, n="fk_offset_" + jnt)
        grp_flip = cmds.group(em=True, n="fk_flip_" + jnt)
        grp_sdk = cmds.group(em=True, n="fk_sdk_" + jnt)
        if "_r" in jnt.lower():
            ctrl = cmds.circle(n="fk_" + jnt, cy=0, r=2, nr=(0, 1, 0))
            cmds.setAttr(ctrl[0] + ".overrideEnabled", 1)
            cmds.setAttr(ctrl[0] + ".overrideColor", 31)
        elif "_l" in jnt.lower():
            ctrl = cmds.circle(n="fk_" + jnt, cy=0, r=2, nr=(0, 1, 0))
            cmds.setAttr(ctrl[0] + ".overrideEnabled", 1)
            cmds.setAttr(ctrl[0] + ".overrideColor", 18)
        else:
            ctrl = cmds.circle(n="fk_" + jnt, cy=0, r=2, nr=(0, 1, 0))
            cmds.setAttr(ctrl[0] + ".overrideEnabled", 1)
            cmds.setAttr(ctrl[0] + ".overrideColor", 21)

        cmds.select(d=True)
        xjnt = cmds.joint(n="fkx_" + jnt)
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

    # Parent FK linearly
    for joint in jnt_list:
        jd = dict[joint]
        if "tongue1" not in joint.lower():
            cmds.parent("fk_offset_" + jd[3], "fkx_" + jd[4])

    cmds.select(d=True)

    # attach def joints to ctrl jnts
    for jnt in jnt_list:
        cmds.parent(cmds.pointConstraint("fkx_" + jnt, jnt), "face_constraints")
        cmds.parent(cmds.orientConstraint("fkx_" + jnt, jnt), "face_constraints")



