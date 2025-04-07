from shiboken2 import wrapInstance
from PySide2 import QtCore, QtWidgets
import maya.cmds as cmds
from maya import OpenMayaUI
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from PySide2.QtGui import QPixmap, QPalette, QColor
from scripts.autorigger.rig_tools import layout_tools
import functools
from pathlib import Path
import scripts.autorigger.rig_tools as rig
from scripts.autorigger.shared import file_handle, skin_handler


def get_maya_win():
    win_ptr = OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(int(win_ptr), QtWidgets.QMainWindow)


def delete_workspace_control(control):
    if cmds.workspaceControl(control, q=True, exists=True):
        cmds.workspaceControl(control, e=True, close=True)
        cmds.deleteUI(control, control=True)


class MyDockableWindow(MayaQWidgetDockableMixin, QtWidgets.QDialog):
    TOOL_NAME = 'Autorigger'


    def __init__(self, parent=None):
        delete_workspace_control(self.TOOL_NAME + 'WorkspaceControl')

        super(self.__class__, self).__init__(parent=parent)
        self.mayaMainWindow = get_maya_win()
        self.setObjectName(self.__class__.TOOL_NAME)

        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle(self.TOOL_NAME)
        self.resize(200, 200)

        layout_v = QtWidgets.QVBoxLayout()
        # Set the layout of the window.
        self.setLayout(layout_v)

        # Add Tabs
        new_tab = self.create_tabs()

        # Draw UI
        self.create_build_tab(new_tab)
        self.create_tools_tab(new_tab)

    def create_tabs(self):

        tabs = QtWidgets.QTabWidget()
        self.layout().addWidget(tabs)
        # Create Main Layout and set it to the tab
        main_layout = QtWidgets.QVBoxLayout()
        tabs.setLayout(main_layout)
        return tabs

    def checklist_item(self, vlayout, label, action, butlabel="Run"):
        # create line layout
        hbox = QtWidgets.QHBoxLayout()
        hbox.setAlignment(QtCore.Qt.AlignTop)
        vlayout.addLayout(hbox)
        # Checkbox
        widget_checkbox = QtWidgets.QCheckBox(label)
        widget_checkbox.setCheckState(QtCore.Qt.Checked)
        # widget_checkbox.stateChanged.connect(action) # Get back to it later, make it enable/disable
        hbox.addWidget(widget_checkbox)
        # Button
        widget_button = QtWidgets.QPushButton('Run')
        widget_button.clicked.connect(action)
        widget_button.setFixedWidth(40)
        hbox.addWidget(widget_button)
        # Separator
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        vlayout.addWidget(line)

    def file_path_assigner(self, vlayout, label, mode="Both"):
        # Title
        title = QtWidgets.QLabel(label)
        title.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        vlayout.addWidget(title)
        # Horizontal Layout
        hbox = QtWidgets.QHBoxLayout()
        vlayout.addLayout(hbox)
        # Line edit
        line_edit = QtWidgets.QLineEdit()
        line_edit.setPlaceholderText("File path")
        hbox.addWidget(line_edit)
        # Buttons
        button_load = QtWidgets.QPushButton('Load')
        button_save = QtWidgets.QPushButton('Save')

        if mode == "Both":
            hbox.addWidget(button_load)
            hbox.addWidget(button_save)

        elif mode == "Load":
            hbox.addWidget(button_load)

        elif mode == "Save":
            hbox.addWidget(button_save)

        return button_load, button_save, line_edit

    def create_build_tab(self, tabs):


        tab_layout = QtWidgets.QVBoxLayout()
        tab = QtWidgets.QWidget()
        tab.setLayout(tab_layout)
        tabs.addTab(tab, "Build")

        # 01 ----- Save Load Config file
        config_file = self.file_path_assigner(tab_layout, 'Build Configuration File', mode="Both")
        config_file[0].clicked.connect(
            functools.partial(self.load_file_path_action, config_file[2], "Load Build Configuration File"))

        # 02 ----- Build Rig Button
        hbox_2 = QtWidgets.QHBoxLayout()
        tab_layout.addLayout(hbox_2)
        button_build_rig = QtWidgets.QPushButton('Build Rig')
        button_build_rig.clicked.connect(self.default_action)
        hbox_2.addWidget(button_build_rig)

        # Scroll area contents start here

        # Create a scrollable widget
        scrollable_widget = QtWidgets.QWidget()
        scrollable_layout = QtWidgets.QVBoxLayout()
        scrollable_widget.setLayout(scrollable_layout)
        tab_layout.addWidget(scrollable_widget)
        scroll = QtWidgets.QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setWidget(scrollable_widget)
        tab_layout.addWidget(scroll)

        # 03 ----- Load Mesh
        load_mesh = self.file_path_assigner(scrollable_layout, 'Mesh', mode="Load")
        load_mesh[0].clicked.connect(
            functools.partial(self.load_file_path_action, load_mesh[2], "Load Mesh File"))

        # 04 ----- Load Placement
        load_placement = self.file_path_assigner(scrollable_layout, 'Placement', mode="Load")
        load_placement[0].clicked.connect(functools.partial(self.load_file_path_action, load_placement[2], "Load Placement File"))

        # 05 ----- Load Skin Weights
        load_skin_weigths = self.file_path_assigner(scrollable_layout, 'Skin Weights', mode="Load")
        load_skin_weigths[0].clicked.connect(
            functools.partial(self.load_file_path_action, load_skin_weigths[2], "Load Skin Weights File"))

        # Separator
        line_1 = QtWidgets.QFrame()
        line_1.setFrameShape(QtWidgets.QFrame.HLine)
        scrollable_layout.addWidget(line_1)

        # 06 ----- Body Rig Module list
        # -- Title
        lb_title_body = QtWidgets.QLabel("Body")
        lb_title_body.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        lb_title_body.setFixedHeight(15)
        scrollable_layout.addWidget(lb_title_body)
        # -- Scroll
        scrollable_widget_body = QtWidgets.QWidget()
        scrollable_layout_body = QtWidgets.QVBoxLayout()
        scrollable_widget_body.setLayout(scrollable_layout_body)
        scrollable_layout.addWidget(scrollable_widget_body)
        scroll_body = QtWidgets.QScrollArea(self)
        scroll_body.setMinimumSize(100, 200)
        scroll_body.setWidgetResizable(True)
        scroll_body.setWidget(scrollable_widget_body)
        scrollable_layout.addWidget(scroll_body)
        # adding each module
        self.checklist_item(scrollable_layout_body, "rig structure", rig.constructor_tools.create_rig_structure)
        self.checklist_item(scrollable_layout_body, "Move meshes", rig.rig_mesh_setup.move_meshes)
        self.checklist_item(scrollable_layout_body, "Deform sctructure", rig.constructor_tools.create_deform_rig)
        self.checklist_item(scrollable_layout_body, "Root rig", functools.partial(self.run_rig_module, rig.rig_root.create_root_rig, joint_dict=True))
        self.checklist_item(scrollable_layout_body, "Torso rig", functools.partial(self.run_rig_module, rig.rig_torso.create_torso_rig, joint_dict=True))
        self.checklist_item(scrollable_layout_body, "Neck rig", functools.partial(self.run_rig_module, rig.rig_neck.create_neck_rig, joint_dict=True, twist=True))
        self.checklist_item(scrollable_layout_body, "Neck rig - No Twist", functools.partial(self.run_rig_module, rig.rig_neck.create_neck_rig, joint_dict=True, twist=False))
        self.checklist_item(scrollable_layout_body, "Arm rig", functools.partial(self.run_rig_module, rig.rig_arm.create_arm_rig, joint_dict=True, twist=True))
        self.checklist_item(scrollable_layout_body, "Arm rig - No Twist", functools.partial(self.run_rig_module, rig.rig_arm.create_arm_rig, joint_dict=True, twist=False))
        self.checklist_item(scrollable_layout_body, "Leg rig", functools.partial(self.run_rig_module, rig.rig_leg.create_leg_rig, joint_dict=True, twist=True))
        self.checklist_item(scrollable_layout_body, "Leg rig - No Twist", functools.partial(self.run_rig_module, rig.rig_leg.create_leg_rig, joint_dict=True, twist=False))
        self.checklist_item(scrollable_layout_body, "Fingers rig", functools.partial(self.run_rig_module, rig.rig_finger.create_finger_rig, joint_dict=True,))
        self.checklist_item(scrollable_layout_body, "Fingers sdk", rig.rig_sdk_finger.create_finger_sdk)

        # Separator
        line_2 = QtWidgets.QFrame()
        line_2.setFrameShape(QtWidgets.QFrame.HLine)
        scrollable_layout.addWidget(line_2)

        # 07 -------- Face base itens
        # -- Title
        lb_title_face = QtWidgets.QLabel("Face")
        lb_title_face.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        lb_title_face.setFixedHeight(15)
        scrollable_layout.addWidget(lb_title_face)

        # Ribbons Skin
        load_ribbons_skins = self.file_path_assigner(scrollable_layout, 'Ribbons Skin Weights', mode="Load")
        # Lattice shapes
        load_lattices_shapes = self.file_path_assigner(scrollable_layout, 'Lattice Shapes', mode="Load")
        # Lattice Skin
        load_lattices_skins = self.file_path_assigner(scrollable_layout, 'Lattice Skin Weights', mode="Load")

        # -- Scroll
        scrollable_widget_face = QtWidgets.QWidget()
        scrollable_layout_face = QtWidgets.QVBoxLayout()
        scrollable_widget_face.setLayout(scrollable_layout_face)
        scrollable_layout.addWidget(scrollable_widget_face)
        scroll_face = QtWidgets.QScrollArea(self)
        scroll_face.setMinimumSize(100, 200)
        scroll_face.setWidgetResizable(True)
        scroll_face.setWidget(scrollable_widget_face)
        scrollable_layout.addWidget(scroll_face)
        # adding each module
        self.checklist_item(scrollable_layout_face, "Face structure", rig.constructor_tools.create_rig_structure_face)
        self.checklist_item(scrollable_layout_face, "Face deform structure", rig.constructor_tools.create_deform_rig_face)
        self.checklist_item(scrollable_layout_face, "Brow rig", functools.partial(self.run_rig_module, rig.rig_facial_brow.create_brow, joint_dict=True))
        self.checklist_item(scrollable_layout_face, "Eyelid rig",
                            functools.partial(self.run_rig_module, rig.rig_facial_eyelid.create_eyelid, joint_dict=True))
        self.checklist_item(scrollable_layout_face, "Nasolabial rig",
                            functools.partial(self.run_rig_module, rig.rig_facial_nasolabial.create_nasolabial,
                                              joint_dict=True))
        self.checklist_item(scrollable_layout_face, "Mouth rig",
                            functools.partial(self.run_rig_module, rig.rig_facial_mouth.create_mouth,
                                              joint_dict=True))
        self.checklist_item(scrollable_layout_face, "Nose rig",
                            functools.partial(self.run_rig_module, rig.rig_facial_nose.create_nose,
                                              joint_dict=True))
        self.checklist_item(scrollable_layout_face, "Cheek rig",
                            functools.partial(self.run_rig_module, rig.rig_facial_cheek.create_cheek,
                                              joint_dict=True))
        self.checklist_item(scrollable_layout_face, "Jaw rig",
                            functools.partial(self.run_rig_module, rig.rig_facial_jaw.create_jaw,
                                              joint_dict=True))
        self.checklist_item(scrollable_layout_face, "Tongue rig",
                            functools.partial(self.run_rig_module, rig.rig_facial_tongue.create_tongue,
                                              joint_dict=True))
        self.checklist_item(scrollable_layout_face, "Eye rig",
                            functools.partial(self.run_rig_module, rig.rig_facial_eye.create_eye,
                                              joint_dict=True))

        self.checklist_item(scrollable_layout_face, "Attach face ribbons", self.attach_face_ribbons)
        self.checklist_item(scrollable_layout_face, "Create face lattices", self.create_face_lattice)
        self.checklist_item(scrollable_layout_face, "Attach face lattices", self.attach_face_lattice)

        # Separator
        line_3 = QtWidgets.QFrame()
        line_3.setFrameShape(QtWidgets.QFrame.HLine)
        scrollable_layout.addWidget(line_3)

        # 08 ----- Misc Module List
        # -- Title
        lb_title_misc = QtWidgets.QLabel("Misc")
        lb_title_misc.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        lb_title_misc.setFixedHeight(15)
        scrollable_layout.addWidget(lb_title_misc)
        # -- Scroll
        scrollable_widget_misc = QtWidgets.QWidget()
        scrollable_layout_misc = QtWidgets.QVBoxLayout()
        scrollable_widget_misc.setLayout(scrollable_layout_misc)
        scrollable_layout.addWidget(scrollable_widget_misc)
        scroll_misc = QtWidgets.QScrollArea(self)
        scroll_misc.setMinimumSize(100, 200)
        scroll_misc.setWidgetResizable(True)
        scroll_misc.setWidget(scrollable_widget_misc)
        scrollable_layout.addWidget(scroll_misc)
        # adding each module
        self.checklist_item(scrollable_layout_misc, "Build all chains", rig.rig_generic_chain.create_chain_all)
        self.checklist_item(scrollable_layout_misc, "Enable scale compensate", self.scale_compensate_enable)
        self.checklist_item(scrollable_layout_misc, "Disable scale compensate", self.scale_compensate_disable)


    def create_tools_tab(self, tabs):
        tab_layout = QtWidgets.QVBoxLayout()
        tab = QtWidgets.QWidget()
        tab.setLayout(tab_layout)
        tabs.addTab(tab, "Tools")

        # Scroll area contents start here
        # Create a scrollable widget
        scrollable_widget = QtWidgets.QWidget()
        scrollable_layout = QtWidgets.QVBoxLayout()
        scrollable_widget.setLayout(scrollable_layout)
        tab_layout.addWidget(scrollable_widget)
        scroll = QtWidgets.QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setWidget(scrollable_widget)
        tab_layout.addWidget(scroll)

        # Grid Layout
        grid_layout_placement = QtWidgets.QGridLayout()
        scrollable_layout.addLayout(grid_layout_placement)
        grid_layout_placement.setAlignment(QtCore.Qt.AlignTop)

        # General Tools
        # Title
        title_general = QtWidgets.QLabel("General Tools")
        grid_layout_placement.addWidget(title_general)

        # Buttons
        button_curve_import = QtWidgets.QPushButton('Import Curve')
        button_curve_import.clicked.connect(functools.partial(file_handle.import_curve, "Load curve", mode="r"))
        grid_layout_placement.addWidget(button_curve_import, 1, 0)
        button_curve_export = QtWidgets.QPushButton('Export Curve')
        button_curve_export.clicked.connect(file_handle.export_curve)
        grid_layout_placement.addWidget(button_curve_export, 1, 1)

        # Separator
        line_1 = QtWidgets.QFrame()
        line_1.setFrameShape(QtWidgets.QFrame.HLine)
        grid_layout_placement.addWidget(line_1, 2, 0, 1, 2)

        # Placement Tools
        # Title
        title_placement = QtWidgets.QLabel("Placement Tools")
        grid_layout_placement.addWidget(title_placement, 3, 0, 1, 2)

        # Buttons
        button_template_body_load = QtWidgets.QPushButton('Load Body Template')
        button_template_body_load.clicked.connect(functools.partial(self.load_joint_placement_template, 'template_humanoid.yaml'))
        grid_layout_placement.addWidget(button_template_body_load)
        button_template_face_load = QtWidgets.QPushButton('Load Face Template')
        button_template_face_load.clicked.connect(functools.partial(self.load_joint_placement_template, 'template_face.yaml'))
        grid_layout_placement.addWidget(button_template_face_load)
        button_placement_load = QtWidgets.QPushButton('Load Placement')
        button_placement_load.clicked.connect(self.load_joint_placement)
        grid_layout_placement.addWidget(button_placement_load)
        button_placement_save = QtWidgets.QPushButton('Save Placement')
        button_placement_save.clicked.connect(rig.layout_tools.joint_layout_save)
        grid_layout_placement.addWidget(button_placement_save)

        # Separator
        line_1 = QtWidgets.QFrame()
        line_1.setFrameShape(QtWidgets.QFrame.HLine)
        grid_layout_placement.addWidget(line_1, 6, 0, 1, 2)

        # Rig Tools
        # Title
        title_rig = QtWidgets.QLabel("Rig Tools")
        title_rig.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        grid_layout_placement.addWidget(title_rig, 7, 0, 1, 2)

        # Ribbon SubTitle
        title_ribbon_ctrls = QtWidgets.QLabel("Ribbon Controls")
        title_ribbon_ctrls.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        grid_layout_placement.addWidget(title_ribbon_ctrls, 8, 0, 1, 2)

        # Buttons
        button_face_rib_attach = QtWidgets.QPushButton('Attach Face Ribbons')
        button_face_rib_attach.clicked.connect(self.attach_face_ribbons)
        grid_layout_placement.addWidget(button_face_rib_attach)
        button_face_rib_detach = QtWidgets.QPushButton('Detach Face Ribbons')
        button_face_rib_detach.clicked.connect(self.detach_face_ribbons)
        grid_layout_placement.addWidget(button_face_rib_detach)
        button_rib_skin_load_sel = QtWidgets.QPushButton('Load Selected Ribbon Skin')
        button_rib_skin_load_sel.clicked.connect(skin_handler.load_selected_skin_yaml)
        grid_layout_placement.addWidget(button_rib_skin_load_sel)
        button_rib_skin_save_sel = QtWidgets.QPushButton('Save Selected Ribbon Skin')
        button_rib_skin_save_sel.clicked.connect(skin_handler.save_selected_skin_yaml)
        grid_layout_placement.addWidget(button_rib_skin_save_sel)

        # Lattice SubTitle
        title_lattice_ctrls = QtWidgets.QLabel("Lattice Controls")
        title_lattice_ctrls.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        grid_layout_placement.addWidget(title_lattice_ctrls, 11, 0, 1, 2)

        # Buttons
        button_face_lat_create = QtWidgets.QPushButton('Create Face Lattices')
        button_face_lat_create.clicked.connect(self.create_face_lattice)
        grid_layout_placement.addWidget(button_face_lat_create, 12, 0, 1, 2)
        button_face_lat_attach = QtWidgets.QPushButton('Attach Face Lattices')
        button_face_lat_attach.clicked.connect(self.attach_face_lattice)
        grid_layout_placement.addWidget(button_face_lat_attach)
        button_face_lat_detach = QtWidgets.QPushButton('Detach Face Lattices')
        button_face_lat_detach.clicked.connect(self.detach_face_lattice)
        grid_layout_placement.addWidget(button_face_lat_detach)
        button_lat_load = QtWidgets.QPushButton('Load Lattice')
        button_lat_load.clicked.connect(rig.layout_tools.lattice_load)
        grid_layout_placement.addWidget(button_lat_load)
        button_lat_save = QtWidgets.QPushButton('Save Lattice')
        button_lat_save.clicked.connect(rig.layout_tools.lattice_save)
        grid_layout_placement.addWidget(button_lat_save)

        # Generic Chain Subtitle
        title_generic_chain = QtWidgets.QLabel("Generic Chain Controls")
        title_generic_chain.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        grid_layout_placement.addWidget(title_generic_chain, 15, 0, 1, 2)

        # Buttons
        button_chain_attr_add = QtWidgets.QPushButton('Add Chain Attr')
        button_chain_attr_add.clicked.connect(self.chain_attr_add)
        grid_layout_placement.addWidget(button_chain_attr_add)
        button_build_chain_selected = QtWidgets.QPushButton('Build Selected Chain(s)')
        button_build_chain_selected.clicked.connect(rig.rig_generic_chain.create_chain_selected)
        grid_layout_placement.addWidget(button_build_chain_selected)
        button_build_chain_all = QtWidgets.QPushButton('Build All Chains')
        button_build_chain_all.clicked.connect(rig.rig_generic_chain.create_chain_all)
        grid_layout_placement.addWidget(button_build_chain_all, 17, 0, 1, 2)

        # Misc Subtitle
        title_misc = QtWidgets.QLabel("Misc")
        title_misc.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        grid_layout_placement.addWidget(title_misc, 18, 0, 1, 2)

        # Buttons
        button_scale_comp_enable = QtWidgets.QPushButton('Enable Scale Compensate')
        button_scale_comp_enable.clicked.connect(self.scale_compensate_enable)
        grid_layout_placement.addWidget(button_scale_comp_enable)
        button_scale_comp_disable = QtWidgets.QPushButton('Disable Scale Compensate')
        button_scale_comp_disable.clicked.connect(self.scale_compensate_disable)
        grid_layout_placement.addWidget(button_scale_comp_disable)

        button_build_rig_body = QtWidgets.QPushButton('Build Basic Body Rig')
        button_build_rig_body.clicked.connect(self.build_rig_body)
        grid_layout_placement.addWidget(button_build_rig_body)

        button_build_rig_body_simple = QtWidgets.QPushButton('Build Basic Simple Body Rig')
        button_build_rig_body_simple.clicked.connect(self.build_rig_body_simple)
        grid_layout_placement.addWidget(button_build_rig_body_simple)

        button_build_rig_face = QtWidgets.QPushButton('Build Face Rig')
        button_build_rig_face.clicked.connect(self.build_rig_face)
        grid_layout_placement.addWidget(button_build_rig_face)


    # Default action
    def default_action(self):
        print("Action executed")

    def scale_compensate_enable(self):
        rig.constructor_tools.set_scale_compensate(attr_value=1)

    def scale_compensate_disable(self):
        rig.constructor_tools.set_scale_compensate(attr_value=0)

    # def set_scale_compensate(self, value=0):
    #     jnt_list = cmds.listRelatives("Root", type="joint", ad=True)
    #     for jnt in jnt_list:
    #         cmds.setAttr(jnt + ".segmentScaleCompensate", value)
    #     cmds.setAttr("Root.segmentScaleCompensate", value)
    def chain_attr_add(self):
        rig.rig_generic_chain.set_chain_start_attr(cmds.ls(sl=True)[0])

    def load_joint_placement(self):
        rig.layout_tools.joint_layout_create(file_handle.file_dialog_yaml("Load joint reference", mode="r"))

    def load_joint_placement_template(self, template_file):
        rig.layout_tools.joint_layout_create(layout_tools.load_template_file(template_file))

    def load_file_path_action(self, line_edit, title):
        # layout_tools.joint_layout_create(fd("Load joint placement", mode="r"))
        dialog = cmds.fileDialog2(bbo=1, cap=title, ds=2, ff="*.yaml;;*.yml", fm=1)
        output = Path(dialog[0])
        line_edit.clear()
        line_edit.setText(dialog[0])

    def run_rig_module(self, module_action, joint_dict=True, twist=None):
        if joint_dict:
            if twist is None:
                module_action(rig.layout_tools.joint_dictionary_creator())
            elif twist == True:
                module_action(rig.layout_tools.joint_dictionary_creator(), twist=True)
            elif twist == False:
                module_action(rig.layout_tools.joint_dictionary_creator(), twist=False)
        else:
            if twist is None:
                module_action()
            elif twist == True:
                module_action(twist=True)
            elif twist == False:
                module_action(twist=False)

    def attach_face_ribbons(self):
        face_controls = 'face_constrain_head'
        face_controls_list = cmds.listRelatives(face_controls)

        if 'brow_control_group' in face_controls_list:
            rig.rig_facial_brow.attach_brow()

        if 'eyelid_control_group' in face_controls_list:
            rig.rig_facial_eyelid.attach_eyelids()

        if 'nasolabial_control_group' in face_controls_list:
            rig.rig_facial_nasolabial.attach_nasolabial()

        if 'mouth_control_group' in face_controls_list:
            rig.rig_facial_mouth.attach_mouth()

    def detach_face_ribbons(self):
        face_controls = 'face_constrain_head'
        face_controls_list = cmds.listRelatives(face_controls)

        if 'brow_control_group' in face_controls_list:
            rig.rig_facial_brow.detach_brow()

        if 'eyelid_control_group' in face_controls_list:
            rig.rig_facial_eyelid.detach_eyelids()

        if 'nasolabial_control_group' in face_controls_list:
            rig.rig_facial_nasolabial.detach_nasolabial()

        if 'mouth_control_group' in face_controls_list:
            rig.rig_facial_mouth.detach_mouth()

    def create_face_lattice(self):
        face_controls = 'face_constrain_head'
        face_controls_list = cmds.listRelatives(face_controls)

        if 'brow_control_group' in face_controls_list:
            rig.rig_facial_brow.create_lattice_brow()

        if 'eyelid_control_group' in face_controls_list:
            rig.rig_facial_eyelid.create_lattice_eyelids()

        if 'nasolabial_control_group' in face_controls_list:
            rig.rig_facial_nasolabial.create_lattice_nasolabial()

        if 'mouth_control_group' in face_controls_list:
            rig.rig_facial_mouth.create_lattice_mouth()

    def attach_face_lattice(self):
        face_controls = 'face_constrain_head'
        face_controls_list = cmds.listRelatives(face_controls)

        if 'brow_control_group' in face_controls_list:
            rig.rig_facial_brow.attach_brow_lattice()

        if 'eyelid_control_group' in face_controls_list:
            rig.rig_facial_eyelid.attach_eyelids_lattice()

        if 'nasolabial_control_group' in face_controls_list:
            rig.rig_facial_nasolabial.attach_nasolabial_lattice()

        if 'mouth_control_group' in face_controls_list:
            rig.rig_facial_mouth.attach_mouth_lattice()

    def detach_face_lattice(self):
        face_controls = 'face_constrain_head'
        face_controls_list = cmds.listRelatives(face_controls)

        if 'brow_control_group' in face_controls_list:
            rig.rig_facial_brow.detach_brow_lattice()

        if 'eyelid_control_group' in face_controls_list:
            rig.rig_facial_eyelid.detach_eyelids_lattice()

        if 'nasolabial_control_group' in face_controls_list:
            rig.rig_facial_nasolabial.detach_nasolabial_lattice()

        if 'mouth_control_group' in face_controls_list:
            rig.rig_facial_mouth.detach_mouth_lattice()

    def build_rig_body(self):
        rig.constructor_tools.create_rig_structure()
        rig.rig_mesh_setup.move_meshes()
        rig.constructor_tools.create_deform_rig()
        rig.rig_root.create_root_rig(layout_tools.joint_dictionary_creator())
        rig.rig_torso.create_torso_rig(layout_tools.joint_dictionary_creator())
        rig.rig_neck.create_neck_rig(layout_tools.joint_dictionary_creator(), twist=True)
        rig.rig_arm.create_arm_rig(layout_tools.joint_dictionary_creator(), twist=True)
        rig.rig_leg.create_leg_rig(layout_tools.joint_dictionary_creator(), twist=True)
        rig.rig_finger.create_finger_rig(layout_tools.joint_dictionary_creator())
        rig.rig_sdk_finger.create_finger_sdk()
        rig.constructor_tools.set_scale_compensate(0)

    def build_rig_body_simple(self):
        rig.constructor_tools.create_rig_structure()
        rig.rig_mesh_setup.move_meshes()
        rig.constructor_tools.create_deform_rig()
        rig.rig_root.create_root_rig(layout_tools.joint_dictionary_creator())
        rig.rig_torso.create_torso_rig(layout_tools.joint_dictionary_creator())
        rig.rig_neck.create_neck_rig(layout_tools.joint_dictionary_creator(), twist=False)
        rig.rig_arm.create_arm_rig(layout_tools.joint_dictionary_creator(), twist=False)
        rig.rig_leg.create_leg_rig(layout_tools.joint_dictionary_creator(), twist=False)
        rig.rig_finger.create_finger_rig(layout_tools.joint_dictionary_creator())
        rig.constructor_tools.set_scale_compensate(0)

    def build_rig_face(self):
        rig.constructor_tools.create_rig_structure_face()
        rig.constructor_tools.create_deform_rig_face()
        rig.rig_facial_brow.create_brow(layout_tools.joint_dictionary_creator())
        rig.rig_facial_eyelid.create_eyelid(layout_tools.joint_dictionary_creator())
        rig.rig_facial_nasolabial.create_nasolabial(layout_tools.joint_dictionary_creator())
        rig.rig_facial_mouth.create_mouth(layout_tools.joint_dictionary_creator())
        rig.rig_facial_nose.create_nose(layout_tools.joint_dictionary_creator())
        rig.rig_facial_cheek.create_cheek(layout_tools.joint_dictionary_creator())
        rig.rig_facial_jaw.create_jaw(layout_tools.joint_dictionary_creator())
        rig.rig_facial_tongue.create_tongue(layout_tools.joint_dictionary_creator())
        rig.rig_facial_eye.create_eye(layout_tools.joint_dictionary_creator())
        rig.constructor_tools.set_scale_compensate(0)


def show():
    my_win = MyDockableWindow()
    my_win.show(dockable=True)

