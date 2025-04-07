import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QFrame
from Rig.Tools import layout_tools
from System.file_handle import file_dialog_yaml as fd
from maya import OpenMayaUI as omui
from shiboken6 import wrapInstance


class MainWindow(QFrame):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        button_load_placement = QPushButton("Load Placement")
        button_load_placement.clicked.connect(self.load_placement)

        # Set the central widget of the Window.
        self.setCentralWidget(button_load_placement)

    def load_placement(self):
        layout_tools.joint_layout_create(fd("Load joint reference", mode="r"))


def toolshelf_open():
    mw_ptr = omui.MQtUtil.mainWindow()
    mayaMainWindow = wrapInstance(int(mw_ptr), QMainWindow)

    app = QApplication(sys.argv)

    toolshelf = MainWindow()
    toolshelf.setObjectName("Autorig")
    toolshelf.setWindowFlags(Qt.Window)  # Make this widget a parented standalone window
    toolshelf.show()
    toolshelf = None  # widget is parented, so it will not be destroyed.

