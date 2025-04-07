import maya.cmds as cmds
import yaml
import os
from pathlib import Path
import io
from definitions import ROOT_DIR
from System.file_handle import file_dialog_yaml


def joint_layout_save():
    """Stores all joint data from current scene"""
    # create empty joint dictionary to store joints data
    joint_data = joint_dictionary_creator()
    # Now run a function to save all hieararchy relationships between joints and store into another dictionary
    hierarchy_dict = {}
    hierarchy_store("joint_reference", hierarchy_dict)
    # combine both joint data and joint hierarchy dictionaries into a single dictionary to save.
    combined_data = {"joints": joint_data, "hierarchy": hierarchy_dict}
    # Prompt a save dialog window for the user to save the information into a YAML file
    file_dialog_yaml("Save joint references", mode="w", saved_data=combined_data)
    # saved_file = cmds.fileDialog2(bbo=1, cap="Save joint references", ds=2, ff="*.yaml;;*.yml", fm=0)
    # output = Path(saved_file[0])
    # with io.open(output, "w") as stream:
    #     yaml.dump(combined_data, stream, default_flow_style=False, allow_unicode=True)


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
        cmds.parent(children, parent_item)
        hierarchy_load(child_tree)


# def load_reference_file():
#     """Prompt an open dialog window to for the user to select a Yaml file to open"""
#     loaded_data = file_dialog_yaml("Load joint reference", mode="r")
#     # opened_file = cmds.fileDialog2(bbo=1, cap="Load joint reference", ds=2, ff="*.yaml;;*.yml", fm=1)
#     # output = Path(opened_file[0])
#     # with open(output, "r") as stream:
#     #     loaded_data = yaml.load(stream, Loader=yaml.FullLoader)
#     return loaded_data


def load_template_file():
    """Loads a template joint structure"""
    output = ROOT_DIR + '/Data/Template/template_humanoid.yaml'
    with open(output, "r") as stream:
        loaded_data = yaml.load(stream, Loader=yaml.FullLoader)
    return loaded_data


def joint_layout_create(source_file):
    """Creates a "joints_reference" joint hierarchy from loaded data"""
    # Deletes any pre-existing joints
    if cmds.ls(typ="joint"):
        cmds.error("There are existing joints in the scene. Please delete before creating new joint reference", n=True)
    else:
        jnt_grp = cmds.group(em=True, n="joint_reference")
        cmds.select(d=True)
        # Create each joint based on data dicitonary and assign its values to the deform dictionary
        layout_dict = source_file["joints"]
        for ref_joint in layout_dict:
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
