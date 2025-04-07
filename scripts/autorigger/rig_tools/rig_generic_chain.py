import maya.cmds as cmds
from scripts.autorigger.shared.utils import connect_point_constraint, connect_orient_constraint, mirror_object


def joint_dictionary_local(joint1st):
    """grabs selected joint and its children and creates a dictionary from it"""
    joint_dictionary = {}
    joint_reference = cmds.listRelatives(joint1st, ad=True, type="joint")
    joint_reference.append(joint1st)
    for current_joint in joint_reference:
        # grab jnt name and save it to string
        jnt_name = str(current_joint)
        # get current joint world space position, rotation, rotation order, and its parent joint
        pos = cmds.xform(current_joint, q=True, ws=True, t=True)
        rot = cmds.xform(current_joint, q=True, ws=True, ro=True)
        rot_order = cmds.xform(current_joint, q=True, roo=True)
        try:
            jnt_parent = cmds.listRelatives(current_joint, p=True)[0]
        except:
            jnt_parent = 'noParent'

        # assign current joint to dictionary as a new key and all its variables as list items
        joint_dictionary[jnt_name] = pos, rot, rot_order, jnt_name, jnt_parent
    cmds.select(d=True)
    return joint_dictionary


def create_chain_rig(dict, joint1st):
    # List all necessary joints
    chain_joints = cmds.listRelatives(joint1st, ad=True, type="joint")
    chain_joints.append(joint1st)
    chain_parent = cmds.listRelatives(joint1st, p=True)[0]
    # Create FK rig
    for joint in chain_joints:
        jd = dict[joint]
        grp_offset = cmds.group(n="fk_offset_" + jd[3], em=True)
        grp_sdk = cmds.group(n="fk_sdk_" + jd[3], em=True)
        grp_flip = cmds.group(n="fk_flip_" + jd[3], em=True)

        ctrl = cmds.circle(n="fk_" + jd[3], cy=-1, r=8, nr=(0, 1, 0))[0]
        if "_l" in joint.lower():
            mirror_object(ctrl, "x")
            mirror_object(ctrl, "y")
            mirror_object(ctrl, "z")
            cmds.setAttr(ctrl + ".overrideEnabled", 1)
            cmds.setAttr(ctrl + ".overrideColor", 6)
        else:
            cmds.setAttr(ctrl + ".overrideEnabled", 1)
            cmds.setAttr(ctrl + ".overrideColor", 13)

        cmds.setAttr(ctrl + ".v", lock=True, k=False, cb=False)
        cmds.select(d=True)
        jnt = cmds.joint(n="fkx_" + jd[3])
        cmds.setAttr(jnt + ".drawStyle", 2)
        cmds.select(d=True)
        cmds.parent(jnt, ctrl)
        cmds.parent(ctrl, grp_flip)
        cmds.parent(grp_flip, grp_sdk)
        cmds.parent(grp_sdk, grp_offset)
        cmds.xform(grp_offset, ws=True, t=jd[0], ro=jd[1], roo=jd[2])

    # Parent FK linearly
    for joint in chain_joints:
        jd = dict[joint]
        if joint1st not in joint:
            cmds.parent("fk_offset_" + jd[3], "fkx_" + jd[4])

    cmds.select(d=True)

    # First Joint additional groups if it has a parent and wants to have global constraint
    if chain_parent:
        grp_fk_chain_master = cmds.group(em=True, n="fk_master_{0}".format(joint1st))
        grp_fk_chain_local = cmds.group(em=True, n="fk_follow_local_{0}".format(joint1st))
        grp_fk_chain_global = cmds.group(em=True, n="fk_follow_global_{0}".format(joint1st))
        grp_fk_chain_flw = cmds.group(em=True, n="fk_follow_{0}".format(joint1st))
        cmds.parent(grp_fk_chain_local, grp_fk_chain_master)
        cmds.parent(grp_fk_chain_global, grp_fk_chain_master)
        cmds.parent(grp_fk_chain_flw, grp_fk_chain_master)
        cmds.matchTransform(grp_fk_chain_master, joint1st)
        # Create Global system groups
        grp_gl_off_chain = cmds.group(em=True, n="global_offset_{0}".format(joint1st))
        grp_gl_chain = cmds.group(em=True, n="global_{0}".format(joint1st))
        cmds.parent(grp_gl_chain, grp_gl_off_chain)
        cmds.matchTransform(grp_gl_off_chain, joint1st)
        cmds.parent(grp_gl_off_chain, "global_constraint_main")
        # Create global attribute on fk chain first ctrl
        cmds.addAttr("fk_{0}".format(joint1st), longName="global", attributeType="double", min=0, max=1, dv=0)
        cmds.setAttr("fk_{0}".format(joint1st) + ".global", e=True, channelBox=True)
        cmds.setAttr("fk_{0}".format(joint1st) + ".global", 1)
        # Constrain the fk chain to both follow local target and follow global
        connect_orient_constraint(grp_fk_chain_flw, grp_fk_chain_local, grp_fk_chain_global, "fk_" + joint1st + ".global")
        cmds.parent("fk_offset_{0}".format(joint1st), grp_fk_chain_flw)
        # Constraint global to globalsystem and follow local to parent joint
        cmds.orientConstraint(grp_gl_chain, grp_fk_chain_global, mo=True, n="follow_global_{0}".format(joint1st))
        cmds.orientConstraint(chain_parent, grp_fk_chain_local, mo=True, n="follow_local_{0}".format(joint1st))

        # Special check if the chain parent is the actual Root joint, or any other joint that does not have a "fkx_" joint prefix
        fkx_chain = "fkx_" + chain_parent
        if cmds.objExists(fkx_chain):
            cmds.parent(grp_fk_chain_master, fkx_chain)
        else:
            cmds.parent(grp_fk_chain_master, "fk_constraint_root")


    # Connect both fk ik rigs to def joints through pont/orient constraint workflow
    for jnt in chain_joints:
        point_constraint = cmds.pointConstraint("fkx_" + jnt, jnt)
        cmds.parent(point_constraint, "constraints")
        orient_constraint = cmds.orientConstraint("fkx_" + jnt, jnt)
        cmds.parent(orient_constraint, "constraints")


def set_chain_start_attr(target):
    cmds.addAttr(target, longName="chain_start", attributeType="bool", dv=True)
    cmds.setAttr(target + ".chain_start", e=True, channelBox=True)


def create_chain_selected():
    first_joint = cmds.ls(sl=True)[0]
    if not cmds.attributeQuery('chain_start', n=first_joint, ex=True):
        set_chain_start_attr(first_joint)
    joint_data = joint_dictionary_local(first_joint)
    create_chain_rig(joint_data, first_joint)


def create_chain_all():
    marked_joints = []
    jnts = cmds.ls(type='joint')
    for jnt in jnts:
        if cmds.attributeQuery('chain_start', n=jnt, ex=True):
            marked_joints.append(jnt)
    for first_joint in marked_joints:
        joint_data = joint_dictionary_local(first_joint)
        create_chain_rig(joint_data, first_joint)
