import maya.cmds as cmds
import yaml
from scripts.autorigger.resources.definitions import ROOT_DIR
from scripts.autorigger.shared.file_handle import file_dialog_yaml
import pymel.core as pm


def joint_layout_save():
    """Stores all joint data from current scene"""
    # select first joint and store
    parent_selected = cmds.ls(sl=True)[0]
    # check if first parent is a joint
    if parent_selected:
        if cmds.objectType(parent_selected) == 'joint':
            # creates a group if the joint hierarchy is loose
            grp = cmds.group(name='Placement', em=True)
            cmds.parent(parent_selected, grp)
            parent_selected = grp

    # create empty joint dictionary to store joints data
    joint_data = joint_dictionary_creator_source(parent_selected)
    # Now run a function to save all hieararchy relationships between joints and store into another dictionary
    hierarchy_dict = {}
    hierarchy_store(parent_selected, hierarchy_dict)
    # combine both joint data and joint hierarchy dictionaries into a single dictionary to save.
    combined_data = {"joints": joint_data, "hierarchy": hierarchy_dict}
    # Prompt a save dialog window for the user to save the information into a YAML file
    file_dialog_yaml("Save joint references", mode="w", saved_data=combined_data)

    # after process is done, check again if first object is not a joint and unparent the root back to world
    if cmds.objectType(parent_selected) != 'joint':
        first_joint = cmds.listRelatives(parent_selected, type='joint')[0]
        cmds.parent(first_joint, world=True)
        # delete old group
        cmds.delete(parent_selected)


def hierarchy_store(parent, tree_dict):
    """Grabs all hierarchy info and saves into a dictionary"""
    children = cmds.listRelatives(parent, c=True, type='transform')
    if children:
        tree_dict[parent] = (children, {})
        for child in children:
            hierarchy_store(child, tree_dict[parent][1])


def hierarchy_load(tree_dict):
    """Loads hierarchy info from a provided dictionary"""
    for parent_item, data in tree_dict.items():
        children, child_tree = data
        if cmds.objExists(parent_item):
            cmds.parent(children, parent_item)
        hierarchy_load(child_tree)


def load_template_file(filename):
    """Loads a template joint structure"""
    output = ROOT_DIR + '/data/template/' + filename
    with open(output, "r") as stream:
        loaded_data = yaml.load(stream, Loader=yaml.FullLoader)
    return loaded_data


def joint_layout_create(source_file):
    """Creates a "joints_reference" joint hierarchy from loaded data"""
    # jnt_grp = cmds.group(em=True, n="joint_reference")
    cmds.select(d=True)
    # Create each joint based on data dicitonary and assign its values to the deform dictionary
    layout_dict = source_file["joints"]
    for ref_joint in layout_dict:
        joint_name = layout_dict[ref_joint][3]
        if cmds.objExists(joint_name):
            # new_joint = cmds.joint(name=layout_dict[ref_joint][3] + "_1")
            print(f"{layout_dict[ref_joint][3]} already exists, skipping joint")
            # print("skip")
        else:
            new_joint = cmds.joint(name=layout_dict[ref_joint][3])
        cmds.xform(new_joint, ws=True, t=layout_dict[ref_joint][0], ro=layout_dict[ref_joint][1],
                   roo=layout_dict[ref_joint][2])
        cmds.select(d=True)
    # Reparent the newly created joints based on the hierarchy data from file.
    hirearchy_tree = source_file["hierarchy"]
    hierarchy_load(hirearchy_tree)
    cmds.select(d=True)


def joint_dictionary_creator():
    """Grabs all joints and creates a dictionary from it"""
    joint_dictionary = {}
    joint_reference = cmds.ls(type="joint")
    for current_joint in joint_reference:
        # grab jnt name and save it to string
        jnt_name = str(current_joint)
        # get current joint world space position, rotation, rotation order, and its parent joint
        pos = cmds.xform(current_joint, q=True, ws=True, t=True)
        rot = cmds.xform(current_joint, q=True, ws=True, ro=True)
        rot_order = cmds.xform(current_joint, q=True, roo=True)
        jnt_parent = cmds.listRelatives(current_joint, p=True)[0]
        # assign current joint to dictionary as a new key and all its variables as list items
        joint_dictionary[jnt_name] = pos, rot, rot_order, jnt_name, jnt_parent
    cmds.select(d=True)
    return joint_dictionary


def joint_dictionary_creator_source(parent):
    """Grabs all joints and creates a dictionary from it"""
    joint_dictionary = {}
    joint_reference = cmds.listRelatives(parent, ad=True, type="joint")
    for current_joint in joint_reference:
        # grab jnt name and save it to string
        jnt_name = str(current_joint)
        # get current joint world space position, rotation, rotation order, and its parent joint
        pos = cmds.xform(current_joint, q=True, ws=True, t=True)
        rot = cmds.xform(current_joint, q=True, ws=True, ro=True)
        rot_order = cmds.xform(current_joint, q=True, roo=True)
        jnt_parent = cmds.listRelatives(current_joint, p=True)[0]
        # assign current joint to dictionary as a new key and all its variables as list items
        joint_dictionary[jnt_name] = pos, rot, rot_order, jnt_name, jnt_parent
    cmds.select(d=True)
    return joint_dictionary

# TODO: Check lattice divisions and make sure the selected lattice matches the number of the loaded lattice

def lattice_save():
    """save selected lattice to yaml file"""
    dict = {}
    lattice = pm.selected()[0]
    lat_obj = cmds.ls(sl=True)[0]
    lattice_pos = cmds.xform(lat_obj, q=True, t=True, ws=True)
    lattice_rot = cmds.xform(lat_obj, q=True, ro=True, ws=True)
    for index, point in enumerate(lattice.pt):
        list = []
        list.append(pm.pointPosition(point)[0])
        list.append(pm.pointPosition(point)[1])
        list.append(pm.pointPosition(point)[2])
        item = str(point)[len(str(point)) - 11:len(str(point))]
        dict[item] = list
    combined_data = {"lattice_dict": dict, "lattice_pos": lattice_pos, "lattice_rot": lattice_rot}
    file_dialog_yaml("Save Lattice", mode="w", saved_data=combined_data)


def lattice_load(file=None):
    """load lattice data from yaml and apply to current lattice"""
    if file is None:
        source_file = file_dialog_yaml("Load Lattice", mode="r")
    else:
        output = ROOT_DIR + '/data/template/' + file
        with open(output, "r") as stream:
            source_file = yaml.load(stream, Loader=yaml.FullLoader)
    lattice = pm.selected()[0]
    lat_obj = cmds.ls(sl=True)[0]
    cmds.xform(lat_obj, t=source_file["lattice_pos"], ws=True)
    cmds.xform(lat_obj, ro=source_file["lattice_rot"], ws=True)
    dict = source_file["lattice_dict"]
    for key in dict:
        cmds.select(str(lattice) + "." + key, r=True)
        cmds.move(dict[key][0], dict[key][1], dict[key][2], ws=True)

