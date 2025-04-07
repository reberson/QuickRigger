import maya.cmds as cmds
import re


def unlock_all_attributes(transform_node):
    # Get all the attributes of the transform node
    attributes = cmds.listAttr(transform_node, locked=True)

    # Unlock each attribute by setting the lock to False
    if attributes:
        for attr in attributes:
            cmds.setAttr(f"{transform_node}.{attr}", lock=False)


def mirror_control_selected(direction='RightToLeft'):
    # List the selected control
    control_names_selected = cmds.ls(sl=True)
    # move controls to new list
    control_names = []
    # check which side to use as mirror point
    if direction == 'RightToLeft':
        control_names = control_names_selected

    else:
        for control_name in control_names_selected:
            # Regex pattern to match "_L", "_R", or "_M" at the end of the string
            match = re.search(r'_(L|R)$', control_name)
            # Invert the list to use the other side
            if match:
                # Split the name at the suffix
                if "_r" in control_name.lower():
                    control_names.append(control_name[:match.start()] + '_L')
                elif "_l" in control_name.lower():
                    control_names.append(control_name[:match.start()] + '_R')
            else:
                control_names.append(control_name)

    # Check if it's a sided control or a single one
    isSided = True

    for control_name in control_names:
        # Regex pattern to match "_L", "_R", or "_M" at the end of the string
        match = re.search(r'_(L|R|M)$', control_name)

        # delete history
        cmds.delete(control_name, constructionHistory=True)

        if match:
            # Split the name at the suffix
            if "_r" in control_name.lower():
                control_other_side = control_name[:match.start()] + '_L'
                isSided = True
            elif "_l" in control_name.lower():
                control_other_side = control_name[:match.start()] + '_R'
                isSided = True
            elif "_m" in control_name.lower():
                control_other_side = control_name
                isSided = False
        else:
            control_other_side = control_name
            isSided = False

        if isSided:
            # Duplicate the other side control
            duplicated_control = cmds.duplicate(control_other_side, name=control_name + '_mirror', rc=True)[0]

            # Unlock attrs from mirror control
            unlock_all_attributes(duplicated_control)

            # Create new empty group
            grp = cmds.group(em=True, p=control_other_side)

            # Parent duplicated control to new group
            cmds.parent(duplicated_control, grp)

            # Unparent group
            cmds.parent(grp, world=True)
            # Send duplicated group to origin
            cmds.xform(grp, t=(0, 0, 0), ws=True)

            # Get position of original control
            pos = cmds.xform(control_name, q=True, t=True, ws=True)

            # Create another group to mirror
            grp_mirror = cmds.group(em=True)

            # Parent the initial group to this one
            cmds.parent(grp, grp_mirror)

            # Scale the new group -1 in X
            cmds.xform(grp_mirror, s=(-1, 1, 1), ws=True, a=True)

            # Move the new group to the control pos
            cmds.xform(grp_mirror, t=pos, ws=True)

            # Grab original control parent
            parent_grp = cmds.listRelatives(control_name, p=True)

            # Parent mirror group to this parent
            cmds.parent(grp_mirror, parent_grp)

            # Parent the duplicate control to this parent directly
            cmds.parent(duplicated_control, parent_grp)

            # Unlock attr
            unlock_all_attributes(duplicated_control)

            # List old curves from original control
            curve_shapes_old = cmds.listRelatives(control_name, shapes=True)

            # Delete old shape curves
            cmds.delete(curve_shapes_old)

            # Delete history of the original control
            cmds.delete(control_name, constructionHistory=True)

            # Freeze duplicate control here
            cmds.makeIdentity(duplicated_control, apply=True, translate=True, rotate=True, scale=True)

            curve_shapes_mirror = cmds.listRelatives(duplicated_control, shapes=True)
            # Reparent each curve to the initial control
            for curve_mirror in curve_shapes_mirror:
                cmds.parent(curve_mirror, control_name, s=True, r=True)
                cmds.delete(curve_mirror, constructionHistory=True)

            # Delete created group
            cmds.delete(grp_mirror)

            # Delete created group
            cmds.delete(duplicated_control)

        else:
            # Duplicate the curve
            duplicated_curve = cmds.duplicate(control_name)[0]
            # Set the scale for mirroring
            cmds.setAttr(duplicated_curve + '.scaleX', -1)

            # Freeze transformations on the duplicated curve
            cmds.makeIdentity(duplicated_curve, apply=True, translate=True, rotate=True, scale=True)

            # Get the shapes of the duplicated curve
            duplicated_shapes = cmds.listRelatives(duplicated_curve, shapes=True, fullPath=True)

            # Parent the shapes of the duplicated curve under the original curve
            for shape in duplicated_shapes:
                cmds.parent(shape, control_name, shape=True, relative=True)

            # Delete the empty transform of the duplicated curve
            cmds.delete(duplicated_curve)

            # Combine all shapes under the original curve if there are multiple segments
            curve_shapes = cmds.listRelatives(control_name, shapes=True, fullPath=True)

    cmds.select(d=True)
