import maya.cmds as cmds
import maya.mel as mel
import Rig
from Rig.Tools import layout_tools
from Rig.Tools import constructor_tools
from Rig.Tools import rig_root, rig_torso, rig_arm, rig_leg, rig_finger, rig_sdk_finger, rig_neck
from Rig.Tools import rig_facial_brow, rig_facial_eyelid
from System.file_handle import file_dialog_yaml as fd
from System.file_handle import export_curve, import_curve
import System.utils


def menu():
    menu_name = 'AutoRigger'
    main_window = mel.eval('$x = $gMainWindow')

    if cmds.menu(menu_name, exists=True):
        cmds.menu(menu_name, e=True, dai=True)
    else:
        cmds.setParent(main_window)
        cmds.menu(menu_name, p=main_window, l=menu_name, tearOff=True, allowOptionBoxes=True)

    cmds.setParent(menu_name, menu=True)

    # Layout Menu
    cmds.menuItem('layout', p=menu_name, l='Layout', subMenu=True, tearOff=True)

    # Reference Menu -- Actions
    cmds.menuItem(p='layout', l='Save layout data', stp='python',
                  c=lambda *args: layout_tools.joint_layout_save(),
                  ann='Save layout joints into YAML')

    cmds.menuItem(p='layout', l='Load layout data', stp='python',
                  c=lambda *args: layout_tools.joint_layout_create(fd("Load joint reference", mode="r")),
                  ann='Load layout joints from file')


    cmds.menuItem(p='layout', l='Load body template', stp='python',
                  c=lambda *args: layout_tools.joint_layout_create(layout_tools.load_template_file('template_humanoid.yaml')),
                  ann='Load a template body rig structure')

    cmds.menuItem(p='layout', l='Load face template', stp='python',
                  c=lambda *args: layout_tools.joint_layout_create(layout_tools.load_template_file('template_face.yaml')),
                  ann='Load a template face rig structure')

    # Rig builder
    cmds.menuItem('builder', p=menu_name, l='Builder', subMenu=True, tearOff=True)

    # Rig body
    cmds.menuItem('body', p='builder', l='Body', subMenu=True, tearOff=True)

    # Rig body - build -- Main Action
    cmds.menuItem(p='body', l='Build rig', stp='python',
                  c=lambda *args: build_rig(),
                  ann='Generates the complete rig based on reference joints')

    # Rig body - build -- Step by step actions
    cmds.menuItem('steps', p='body', l='Step by step', subMenu=True, tearOff=True)

    cmds.menuItem(p='steps', l='Create rig structure', stp='python',
                  c=lambda *args: constructor_tools.create_rig_structure(),
                  ann='Creates the structure for the rig')

    cmds.menuItem(p='steps', l='Create deform', stp='python',
                  c=lambda *args: constructor_tools.create_deform_rig(),
                  ann='Creates a complete deformation rig')

    cmds.menuItem(p='steps', l='Create root rig', stp='python',
                  c=lambda *args: rig_root.create_root_rig(layout_tools.joint_dictionary_creator()),
                  ann='Creates the rig controls for the root')

    cmds.menuItem(p='steps', l='Create torso rig', stp='python',
                  c=lambda *args: rig_torso.create_torso_rig(layout_tools.joint_dictionary_creator()),
                  ann='Creates the rig controls for the torso')

    cmds.menuItem(p='steps', l='Create neck rig', stp='python',
                  c=lambda *args: rig_neck.create_neck_rig(layout_tools.joint_dictionary_creator()),
                  ann='Creates the rig controls for the neck')

    cmds.menuItem(p='steps', l='Create arm rig', stp='python',
                  c=lambda *args: rig_arm.create_arm_rig(layout_tools.joint_dictionary_creator()),
                  ann='Creates the rig controls for the arms')

    cmds.menuItem(p='steps', l='Create leg rig', stp='python',
                  c=lambda *args: rig_leg.create_leg_rig(layout_tools.joint_dictionary_creator()),
                  ann='Creates the rig controls for the legs')

    cmds.menuItem(p='steps', l='Create fingers rig', stp='python',
                  c=lambda *args: rig_finger.create_finger_rig(layout_tools.joint_dictionary_creator()),
                  ann='Creates the rig controls for the fingers')

    cmds.menuItem(p='steps', l='Create fingers sdk', stp='python',
                  c=lambda *args: rig_sdk_finger.create_finger_sdk(),
                  ann='Creates the sdk controls for fingers')

    # Rig face
    cmds.menuItem('face', p='builder', l='Face', subMenu=True, tearOff=True)

    # Rig face - build -- Main Action
    cmds.menuItem(p='face', l='Build face rig', stp='python',
                  c=lambda *args: build_rig_face(),
                  ann='Generates the complete face rig based on reference joints')

    # Rig face - Steps
    cmds.menuItem('facesteps', p='face', l='Step by step', subMenu=True, tearOff=True)

    cmds.menuItem(p='facesteps', l='face structure', stp='python',
                  c=lambda *args: constructor_tools.create_rig_structure_face(),
                  ann='Creates the base structure for face rig')

    cmds.menuItem(p='facesteps', l='face deform', stp='python',
                  c=lambda *args: constructor_tools.create_deform_rig_face(),
                  ann='Creates a complete deformation rig')

    cmds.menuItem(p='facesteps', l='brow rig', stp='python',
                  c=lambda *args: rig_facial_brow.create_brow(layout_tools.joint_dictionary_creator()),
                  ann='Creates the rig controls for the brow')

    cmds.menuItem(p='facesteps', l='eyelid rig', stp='python',
                  c=lambda *args: rig_facial_eyelid.create_eyelid(layout_tools.joint_dictionary_creator()),
                  ann='Creates the rig controls for the brow')



    # Rig face - Tools
    cmds.menuItem('facetools', p='face', l='Face Tools', subMenu=True, tearOff=True)
    cmds.menuItem(p='facetools', l='Attach Brow', stp='python',
                  c=lambda *args: rig_facial_brow.attach_brow(),
                  ann='Attach brow control to ribbon')
    cmds.menuItem(p='facetools', l='Detach Brow', stp='python',
                  c=lambda *args: rig_facial_brow.detach_brow(),
                  ann='Detach brow control from ribbon')

    # Tools Menu
    cmds.menuItem('tools', p=menu_name, l='Tools', subMenu=True, tearOff=True)

    # Tools Menu -- Actions
    cmds.menuItem(p='tools', l='Export curve', stp='python',
                  c=lambda *args: export_curve(),
                  ann='Save curve object into YAML')

    cmds.menuItem(p='tools', l='Import curve', stp='python',
                  c=lambda *args: import_curve(fd("Load curve", mode="r")),
                  ann='Load curve object into YAML')


def build_rig():
    constructor_tools.create_rig_structure()
    constructor_tools.create_deform_rig()
    rig_root.create_root_rig(layout_tools.joint_dictionary_creator())
    rig_torso.create_torso_rig(layout_tools.joint_dictionary_creator())
    rig_neck.create_neck_rig(layout_tools.joint_dictionary_creator())
    rig_arm.create_arm_rig(layout_tools.joint_dictionary_creator())
    rig_leg.create_leg_rig(layout_tools.joint_dictionary_creator())
    rig_finger.create_finger_rig(layout_tools.joint_dictionary_creator())
    rig_sdk_finger.create_finger_sdk()


def build_rig_face():
    constructor_tools.create_rig_structure_face()
    constructor_tools.create_deform_rig_face()
    rig_facial_brow.create_brow(layout_tools.joint_dictionary_creator())
    rig_facial_eyelid.create_eyelid(layout_tools.joint_dictionary_creator())
