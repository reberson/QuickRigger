import maya.cmds as cmds

# TODO: Refactor to Class objects
# TODO: Limit translation for the sdk control, also lock other stuff that wont be used
# TODO: make list comprehension to be reusable and generic
# TODO: Add control for finger spread
# TODO: hide the attributes on the holder, since they are overriden whenever we move the shape control. Or we can add another attribute that controls the shape
# TODO: add visibility toggle attribute for the control
# TODO: Hide Movex and movey attributes from channelbox


def create_finger_sdk():
    sides = ["_R", "_L"]
    for side in sides:
        grp_constraint = cmds.group(em=True, n="parentconstraint_sdk_fingers{0}".format(side))
        grp_flip = cmds.group(em=True, n="flip_sdk_fingers{0}".format(side))
        grp_holder = cmds.group(em=True, n="offset_holder_sdk_fingers{0}".format(side))
        ctrl_holder = cmds.circle(n="holder_sdk_fingers{0}".format(side), r=10, nr=(0, 1, 0))
        grp_ctrl = cmds.group(em=True, n="offset_cntrl_sdk_fingers{0}".format(side))
        ctrl = cmds.circle(n="cntrl_sdk_fingers{0}".format(side), r=2, nr=(0, 1, 0))  # Define the object that will hold the switch attribute.

        # create metacarpal ctrl
        grp_offset_metacarpal = cmds.group(em=True, n="offset_metacarpal{0}".format(side))
        grp_extra_metacarpal = cmds.group(em=True, n="extra_metacarpal{0}".format(side))
        ctrl_metacarpal = cmds.circle(n="cntrl_metacarpal{0}".format(side), r=4, nr=(0, 0, 1))

        cmds.parent(ctrl[0], grp_ctrl)
        cmds.parent(grp_ctrl, ctrl_holder[0])
        cmds.parent(ctrl_holder[0], grp_holder)
        cmds.parent(grp_holder, grp_flip)
        cmds.parent(grp_flip, grp_constraint)
        cmds.parent(grp_extra_metacarpal, grp_offset_metacarpal)
        cmds.parent(ctrl_metacarpal[0], grp_extra_metacarpal)
        cmds.parent(grp_offset_metacarpal, grp_constraint)

        cmds.matchTransform(grp_constraint, "Wrist{0}".format(side))

        if side == "_L":
            cmds.xform(grp_flip, r=True, ro=(180, 0, 180))
            cmds.xform(grp_holder, r=True, t=(0, -25, 0))
            cmds.xform(grp_offset_metacarpal, r=True, t=(-5, -5, 0))
            cmds.xform(grp_offset_metacarpal, r=True, ro=(0, 180, 180))
            cmds.xform(grp_offset_metacarpal, r=True, s=(-1, 1, 1))

        else:
            cmds.xform(grp_holder, r=True, t=(0, 25, 0))
            cmds.xform(grp_offset_metacarpal, r=True, t=(5, 5, 0))

        cmds.parent(grp_constraint, "drivers_system")
        cmds.pointConstraint("Wrist{0}".format(side), grp_constraint)
        cmds.orientConstraint("Wrist{0}".format(side), grp_constraint)

        # define the list of affected joints
        finger_index_list = ["fk_sdk_IndexFinger1{0}".format(side), "fk_sdk_IndexFinger2{0}".format(side), "fk_sdk_IndexFinger3{0}".format(side)]
        finger_index_list_sec = ["fk_sdk_secondary_IndexFinger1{0}".format(side), "fk_sdk_secondary_IndexFinger2{0}".format(side), "fk_sdk_secondary_IndexFinger3{0}".format(side)]
        finger_middle_list = ["fk_sdk_MiddleFinger1{0}".format(side), "fk_sdk_MiddleFinger2{0}".format(side), "fk_sdk_MiddleFinger3{0}".format(side)]
        finger_middle_list_sec = ["fk_sdk_secondary_MiddleFinger1{0}".format(side), "fk_sdk_secondary_MiddleFinger2{0}".format(side), "fk_sdk_secondary_MiddleFinger3{0}".format(side)]
        finger_ring_list = ["fk_sdk_RingFinger1{0}".format(side), "fk_sdk_RingFinger2{0}".format(side), "fk_sdk_RingFinger3{0}".format(side)]
        finger_ring_list_sec = ["fk_sdk_secondary_RingFinger1{0}".format(side), "fk_sdk_secondary_RingFinger2{0}".format(side), "fk_sdk_secondary_RingFinger3{0}".format(side)]
        finger_pinky_list = ["fk_sdk_PinkyFinger1{0}".format(side), "fk_sdk_PinkyFinger2{0}".format(side), "fk_sdk_PinkyFinger3{0}".format(side)]
        finger_pinky_list_sec = ["fk_sdk_secondary_PinkyFinger1{0}".format(side), "fk_sdk_secondary_PinkyFinger2{0}".format(side), "fk_sdk_secondary_PinkyFinger3{0}".format(side)]
        finger_thumb_list = ["fk_sdk_ThumbFinger2{0}".format(side), "fk_sdk_ThumbFinger3{0}".format(side)]

        # create controlling attributes
        cmds.addAttr(ctrl_holder, ln="movex", at="float", keyable=True, min=-10, max=10)
        cmds.addAttr(ctrl_holder, ln="movez", at="float", keyable=True, min=-10, max=10)
        cmds.addAttr(ctrl_holder, ln="spread", at="float", keyable=True, min=-10, max=10)
        cmds.addAttr(ctrl_holder, ln="thumbcurl", at="float", keyable=True, min=-10, max=10)
        cmds.addAttr(ctrl_holder, ln="indexcurl", at="float", keyable=True, min=-10, max=10)
        cmds.addAttr(ctrl_holder, ln="middlecurl", at="float", keyable=True, min=-10, max=10)
        cmds.addAttr(ctrl_holder, ln="ringcurl", at="float", keyable=True, min=-10, max=10)
        cmds.addAttr(ctrl_holder, ln="pinkycurl", at="float", keyable=True, min=-10, max=10)

        # create driven keys for individual curl
        for finger_joint in finger_index_list:
            cmds.setDrivenKeyframe(finger_joint, at="rotateX", cd="holder_sdk_fingers{0}.indexcurl".format(side), dv=-10, v=-90)
            cmds.setDrivenKeyframe(finger_joint, at="rotateX", cd="holder_sdk_fingers{0}.indexcurl".format(side), dv=-0, v=0)
            cmds.setDrivenKeyframe(finger_joint, at="rotateX", cd="holder_sdk_fingers{0}.indexcurl".format(side), dv=10, v=30)

        for finger_joint in finger_middle_list:
            cmds.setDrivenKeyframe(finger_joint, at="rotateX", cd="holder_sdk_fingers{0}.middlecurl".format(side), dv=-10, v=-90)
            cmds.setDrivenKeyframe(finger_joint, at="rotateX", cd="holder_sdk_fingers{0}.middlecurl".format(side), dv=-0, v=0)
            cmds.setDrivenKeyframe(finger_joint, at="rotateX", cd="holder_sdk_fingers{0}.middlecurl".format(side), dv=10, v=30)

        for finger_joint in finger_ring_list:
            cmds.setDrivenKeyframe(finger_joint, at="rotateX", cd="holder_sdk_fingers{0}.ringcurl".format(side), dv=-10, v=-90)
            cmds.setDrivenKeyframe(finger_joint, at="rotateX", cd="holder_sdk_fingers{0}.ringcurl".format(side), dv=-0, v=0)
            cmds.setDrivenKeyframe(finger_joint, at="rotateX", cd="holder_sdk_fingers{0}.ringcurl".format(side), dv=10, v=30)

        for finger_joint in finger_pinky_list:
            cmds.setDrivenKeyframe(finger_joint, at="rotateX", cd="holder_sdk_fingers{0}.pinkycurl".format(side), dv=-10, v=-90)
            cmds.setDrivenKeyframe(finger_joint, at="rotateX", cd="holder_sdk_fingers{0}.pinkycurl".format(side), dv=-0, v=0)
            cmds.setDrivenKeyframe(finger_joint, at="rotateX", cd="holder_sdk_fingers{0}.pinkycurl".format(side), dv=10, v=30)

        for finger_joint in finger_thumb_list:
            cmds.setDrivenKeyframe(finger_joint, at="rotateX", cd="holder_sdk_fingers{0}.thumbcurl".format(side), dv=-10, v=-90)
            cmds.setDrivenKeyframe(finger_joint, at="rotateX", cd="holder_sdk_fingers{0}.thumbcurl".format(side), dv=-0, v=0)
            cmds.setDrivenKeyframe(finger_joint, at="rotateX", cd="holder_sdk_fingers{0}.thumbcurl".format(side), dv=10, v=30)

        # create driven keys for collective curl
        for finger_joint in finger_index_list_sec:
            cmds.setDrivenKeyframe(finger_joint, at="rotateX", cd="holder_sdk_fingers{0}.movex".format(side), dv=-10, v=-90)
            cmds.setDrivenKeyframe(finger_joint, at="rotateX", cd="holder_sdk_fingers{0}.movex".format(side), dv=-0, v=0)
            cmds.setDrivenKeyframe(finger_joint, at="rotateX", cd="holder_sdk_fingers{0}.movex".format(side), dv=10, v=30)

        for finger_joint in finger_middle_list_sec:
            cmds.setDrivenKeyframe(finger_joint, at="rotateX", cd="holder_sdk_fingers{0}.movex".format(side), dv=-10, v=-90)
            cmds.setDrivenKeyframe(finger_joint, at="rotateX", cd="holder_sdk_fingers{0}.movex".format(side), dv=-0, v=0)
            cmds.setDrivenKeyframe(finger_joint, at="rotateX", cd="holder_sdk_fingers{0}.movex".format(side), dv=10, v=30)

        for finger_joint in finger_ring_list_sec:
            cmds.setDrivenKeyframe(finger_joint, at="rotateX", cd="holder_sdk_fingers{0}.movex".format(side), dv=-10, v=-90)
            cmds.setDrivenKeyframe(finger_joint, at="rotateX", cd="holder_sdk_fingers{0}.movex".format(side), dv=-0, v=0)
            cmds.setDrivenKeyframe(finger_joint, at="rotateX", cd="holder_sdk_fingers{0}.movex".format(side), dv=10, v=30)

        for finger_joint in finger_pinky_list_sec:
            cmds.setDrivenKeyframe(finger_joint, at="rotateX", cd="holder_sdk_fingers{0}.movex".format(side), dv=-10, v=-90)
            cmds.setDrivenKeyframe(finger_joint, at="rotateX", cd="holder_sdk_fingers{0}.movex".format(side), dv=-0, v=0)
            cmds.setDrivenKeyframe(finger_joint, at="rotateX", cd="holder_sdk_fingers{0}.movex".format(side), dv=10, v=30)


        # create driven keys for finger spread
        cmds.setDrivenKeyframe("fk_sdk_IndexFinger1{0}".format(side), at="rotateZ", cd="holder_sdk_fingers{0}.spread".format(side), dv=-10, v=-15)
        cmds.setDrivenKeyframe("fk_sdk_IndexFinger1{0}".format(side), at="rotateZ", cd="holder_sdk_fingers{0}.spread".format(side), dv=-0, v=0)
        cmds.setDrivenKeyframe("fk_sdk_IndexFinger1{0}".format(side), at="rotateZ", cd="holder_sdk_fingers{0}.spread".format(side), dv=10, v=20)

        cmds.setDrivenKeyframe("fk_sdk_RingFinger1{0}".format(side), at="rotateZ", cd="holder_sdk_fingers{0}.spread".format(side), dv=-10, v=10)
        cmds.setDrivenKeyframe("fk_sdk_RingFinger1{0}".format(side), at="rotateZ", cd="holder_sdk_fingers{0}.spread".format(side), dv=-0, v=0)
        cmds.setDrivenKeyframe("fk_sdk_RingFinger1{0}".format(side), at="rotateZ", cd="holder_sdk_fingers{0}.spread".format(side), dv=10, v=-10)

        cmds.setDrivenKeyframe("fk_sdk_PinkyFinger1{0}".format(side), at="rotateZ", cd="holder_sdk_fingers{0}.spread".format(side), dv=-10, v=20)
        cmds.setDrivenKeyframe("fk_sdk_PinkyFinger1{0}".format(side), at="rotateZ", cd="holder_sdk_fingers{0}.spread".format(side), dv=-0, v=0)
        cmds.setDrivenKeyframe("fk_sdk_PinkyFinger1{0}".format(side), at="rotateZ", cd="holder_sdk_fingers{0}.spread".format(side), dv=10, v=-15)


        # create driven keys on Y affecting only first joint
        cmds.setDrivenKeyframe("fk_sdk_IndexFinger1{0}".format(side), at="rotateX", cd="holder_sdk_fingers{0}.movez".format(side), dv=-10, v=-45)
        cmds.setDrivenKeyframe("fk_sdk_IndexFinger1{0}".format(side), at="rotateX", cd="holder_sdk_fingers{0}.movez".format(side), dv=-0, v=0)
        cmds.setDrivenKeyframe("fk_sdk_IndexFinger1{0}".format(side), at="rotateX", cd="holder_sdk_fingers{0}.movez".format(side), dv=10, v=30)

        cmds.setDrivenKeyframe("fk_sdk_MiddleFinger1{0}".format(side), at="rotateX", cd="holder_sdk_fingers{0}.movez".format(side), dv=-10, v=-15)
        cmds.setDrivenKeyframe("fk_sdk_MiddleFinger1{0}".format(side), at="rotateX", cd="holder_sdk_fingers{0}.movez".format(side), dv=-0, v=0)
        cmds.setDrivenKeyframe("fk_sdk_MiddleFinger1{0}".format(side), at="rotateX", cd="holder_sdk_fingers{0}.movez".format(side), dv=10, v=10)

        cmds.setDrivenKeyframe("fk_sdk_RingFinger1{0}".format(side), at="rotateX", cd="holder_sdk_fingers{0}.movez".format(side), dv=-10, v=10)
        cmds.setDrivenKeyframe("fk_sdk_RingFinger1{0}".format(side), at="rotateX", cd="holder_sdk_fingers{0}.movez".format(side), dv=-0, v=0)
        cmds.setDrivenKeyframe("fk_sdk_RingFinger1{0}".format(side), at="rotateX", cd="holder_sdk_fingers{0}.movez".format(side), dv=10, v=-15)

        cmds.setDrivenKeyframe("fk_sdk_PinkyFinger1{0}".format(side), at="rotateX", cd="holder_sdk_fingers{0}.movez".format(side), dv=-10, v=30)
        cmds.setDrivenKeyframe("fk_sdk_PinkyFinger1{0}".format(side), at="rotateX", cd="holder_sdk_fingers{0}.movez".format(side), dv=-0, v=0)
        cmds.setDrivenKeyframe("fk_sdk_PinkyFinger1{0}".format(side), at="rotateX", cd="holder_sdk_fingers{0}.movez".format(side), dv=10, v=-45)

        # Below keys makes the controller control the target attribute
        cmds.setDrivenKeyframe("holder_sdk_fingers{0}".format(side), at="movex", cd="cntrl_sdk_fingers{0}.tx".format(side), dv=-10, v=-10)
        cmds.setDrivenKeyframe("holder_sdk_fingers{0}".format(side), at="movex", cd="cntrl_sdk_fingers{0}.tx".format(side), dv=0, v=0)
        cmds.setDrivenKeyframe("holder_sdk_fingers{0}".format(side), at="movex", cd="cntrl_sdk_fingers{0}.tx".format(side), dv=10, v=10)

        cmds.setDrivenKeyframe("holder_sdk_fingers{0}".format(side), at="movez", cd="cntrl_sdk_fingers{0}.tz".format(side), dv=-10, v=-10)
        cmds.setDrivenKeyframe("holder_sdk_fingers{0}".format(side), at="movez", cd="cntrl_sdk_fingers{0}.tz".format(side), dv=0, v=0)
        cmds.setDrivenKeyframe("holder_sdk_fingers{0}".format(side), at="movez", cd="cntrl_sdk_fingers{0}.tz".format(side), dv=10, v=10)

        # create constraints for metacarpal controls
        constraint_orient_metacarpal_pinky = cmds.orientConstraint(grp_extra_metacarpal, ctrl_metacarpal, "fk_sdk_PinkyMeta{0}".format(side), mo=True, n="orient_metacarpal_pinky{0}".format(side))
        cmds.setAttr(constraint_orient_metacarpal_pinky[0] + "." + grp_extra_metacarpal + "W0", 0)
        cmds.setAttr(constraint_orient_metacarpal_pinky[0] + "." + ctrl_metacarpal[0] + "W1", 1)

        constraint_orient_metacarpal_ring = cmds.orientConstraint(grp_extra_metacarpal, ctrl_metacarpal, "fk_sdk_RingMeta{0}".format(side), mo=True, n="orient_metacarpal_ring{0}".format(side))
        cmds.setAttr(constraint_orient_metacarpal_ring[0] + "." + grp_extra_metacarpal + "W0", 0.5)
        cmds.setAttr(constraint_orient_metacarpal_ring[0] + "." + ctrl_metacarpal[0] + "W1", 0.5)

        constraint_orient_metacarpal_middle = cmds.orientConstraint(grp_extra_metacarpal, ctrl_metacarpal, "fk_sdk_MiddleMeta{0}".format(side), mo=True, n="orient_metacarpal_middle{0}".format(side))
        cmds.setAttr(constraint_orient_metacarpal_middle[0] + "." + grp_extra_metacarpal + "W0", 0.75)
        cmds.setAttr(constraint_orient_metacarpal_middle[0] + "." + ctrl_metacarpal[0] + "W1", 0.25)

        # point constraints for metacarpal controls with falloff
        constraint_point_metacarpal_pinky = cmds.pointConstraint(grp_extra_metacarpal, ctrl_metacarpal, "fk_sdk_PinkyMeta{0}".format(side), mo=True, n="point_metacarpal_pinky{0}".format(side))
        cmds.setAttr(constraint_point_metacarpal_pinky[0] + "." + grp_extra_metacarpal + "W0", 0)
        cmds.setAttr(constraint_point_metacarpal_pinky[0] + "." + ctrl_metacarpal[0] + "W1", 1)

        constraint_point_metacarpal_ring = cmds.pointConstraint(grp_extra_metacarpal, ctrl_metacarpal, "fk_sdk_RingMeta{0}".format(side), mo=True, n="point_metacarpal_ring{0}".format(side))
        cmds.setAttr(constraint_point_metacarpal_ring[0] + "." + grp_extra_metacarpal + "W0", 0.5)
        cmds.setAttr(constraint_point_metacarpal_ring[0] + "." + ctrl_metacarpal[0] + "W1", 0.5)

        constraint_point_metacarpal_middle = cmds.pointConstraint(grp_extra_metacarpal, ctrl_metacarpal, "fk_sdk_MiddleMeta{0}".format(side), mo=True, n="point_metacarpal_middle{0}".format(side))
        cmds.setAttr(constraint_point_metacarpal_middle[0] + "." + grp_extra_metacarpal + "W0", 0.75)
        cmds.setAttr(constraint_point_metacarpal_middle[0] + "." + ctrl_metacarpal[0] + "W1", 0.25)



