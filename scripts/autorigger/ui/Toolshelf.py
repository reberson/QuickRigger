from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QApplication, QPushButton, QWidget, QVBoxLayout
from scripts.autorigger.rig_tools import layout_tools
from scripts.autorigger.shared.file_handle import file_dialog_yaml as fd
import maya.OpenMayaUI
from shiboken6 import wrapInstance


def getMayaMainWindow():
    main_window_ptr = maya.OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QMainWindow)


class Toolshelf(QWidget):

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent=parent, *args, **kwargs)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Button to load placement
        self.btn_import_placement = QPushButton('Import Placement', self)
        self.btn_import_placement.clicked.connect(self.import_placement)
        layout.addWidget(self.btn_import_placement)

    def import_placement(self):
        # self._export('skeleton')
        layout_tools.joint_layout_create(fd("Load joint reference", mode="r"))

# def toolshelf_open():
#     mw_ptr = maya.OpenMayaUI.MQtUtil.mainWindow()
#     mayaMainWindow = wrapInstance(int(mw_ptr), QMainWindow)
#
#     app = QApplication(sys.argv)
#
#     toolshelf = MainWindow()
#     toolshelf.setObjectName("Autorig")
#     toolshelf.setWindowFlags(QtCore.Qt.Window)  # Make this widget a parented standalone window
#     toolshelf.show()
#     toolshelf = None  # widget is parented, so it will not be destroyed.


def show():
    global window  # prevent garbage collection
    app = QApplication.instance()
    parent = getMayaMainWindow()
    window = Toolshelf(parent=parent)
    window.setWindowFlags(QtCore.Qt.Window)
    window.setWindowTitle('Autorigger')
    window.resize(400, 200)
    window.show()
