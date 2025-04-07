import sys

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QMainWindow, QMenu, QPushButton

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

    def contextMenuEvent(self, e):
        context = QMenu(self)
        context.addAction(QAction("test 1", self))
        context.addAction(QAction("test 2", self))
        context.addAction(QAction("test 3", self))
        context.exec(e.globalPos())

    def mousePressEvent(self, event):
        print("Mouse pressed!")
        super().mousePressEvent(event)

    class CustomButton(QPushButton):
        def mousePressEvent(self, e):
            e.accept()

    def populate(self, tab):

        # Button
        button_a = QtWidgets.QPushButton('Action 1')
        button_a.clicked.connect(self.default_action)
        tab.addTab(button_a, "Tab 1")
        button_b = QtWidgets.QPushButton('Action 2')
        button_b.clicked.connect(self.default_action)
        tab.addTab(button_b, "Tab 2")

        # Label
        label_a = QtWidgets.QLabel("Label Text")
        label_a_font = label_a.font()
        label_a_font.setPointSize(80)  # doesnt work it seems
        label_a.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.layout().addWidget(label_a)

        # Label as Image
        label_b = QtWidgets.QLabel("")
        label_b.setPixmap(QPixmap("C:/Users/RebersonAlves/Downloads/cat.jpg"))
        label_b.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        label_b.setScaledContents(False)
        self.layout().addWidget(label_b)

        # Checkbox
        checkbox_a = QtWidgets.QCheckBox("Checkbox label a")
        checkbox_a.setCheckState(QtCore.Qt.Checked)
        checkbox_a.stateChanged.connect(self.default_action)
        self.layout().addWidget(checkbox_a)

        # Checkbox Tri State
        checkbox_b = QtWidgets.QCheckBox("Checkbox label a")
        checkbox_b.setCheckState(QtCore.Qt.PartiallyChecked)
        checkbox_b.stateChanged.connect(self.default_action)
        self.layout().addWidget(checkbox_b)

        # Combo box
        combobox_a = QtWidgets.QComboBox()
        combobox_a.addItems(["item a", "item b", "item c"])
        # The default signal from currentIndexChanged sends the index
        combobox_a.currentIndexChanged.connect(self.combobox_index_changed)
        # The same signal can send a text string
        combobox_a.currentTextChanged.connect(self.combobox_text_changed)
        self.layout().addWidget(combobox_a)

        # Combo box Editable
        combobox_b = QtWidgets.QComboBox()
        combobox_b.addItems(["item a", "item b", "item c"])
        # The default signal from currentIndexChanged sends the index
        combobox_b.currentIndexChanged.connect(self.combobox_index_changed)
        # The same signal can send a text string
        combobox_b.currentTextChanged.connect(self.combobox_text_changed)
        combobox_b.setEditable(True)
        combobox_b.setInsertPolicy(QtWidgets.QComboBox.InsertAlphabetically)
        combobox_b.setMaxCount(10)  # limit the maximun of itens if wanted
        self.layout().addWidget(combobox_b)

        # List
        list_a = QtWidgets.QListWidget()
        list_a.addItems(["item a", "item b", "item c"])
        list_a.currentItemChanged.connect(self.list_index_changed)
        list_a.currentTextChanged.connect(self.list_text_changed)
        self.layout().addWidget(list_a)

        # Line Edit
        line_edit_a = QtWidgets.QLineEdit()
        line_edit_a.setMaxLength(10)
        line_edit_a.setPlaceholderText("Placeholder text")
        # line_edit_a.setReadOnly(True) # uncomment this to make readonly
        line_edit_a.returnPressed.connect(self.line_edit_return_pressed)
        line_edit_a.selectionChanged.connect(self.line_edit_selection_changed)
        line_edit_a.textChanged.connect(self.line_edit_text_changed)
        line_edit_a.textEdited.connect(self.line_edit_text_edited)
        self.layout().addWidget(line_edit_a)

        # SpinBox
        spin_box = QtWidgets.QSpinBox()
        spin_box.setMinimum(-10)
        spin_box.setMaximum(100)
        spin_box.setPrefix("$ ")
        spin_box.setSuffix(" Dollars")
        spin_box.setSingleStep(3)
        spin_box.valueChanged.connect(self.value_changed)
        spin_box.textChanged.connect(self.value_changed_str)
        self.layout().addWidget(spin_box)

        # SpinBox Only on controls
        spin_box_b = QtWidgets.QSpinBox()
        spin_box_b.setMinimum(-10)
        spin_box_b.setMaximum(100)
        spin_box_b.setPrefix("$ ")
        spin_box_b.setSuffix(" Dollars")
        spin_box_b.setSingleStep(3)
        spin_box_b.valueChanged.connect(self.value_changed)
        spin_box_b.textChanged.connect(self.value_changed_str)
        spin_box_b.lineEdit().setReadOnly(True)
        self.layout().addWidget(spin_box_b)

        # Double SpinBox
        dspin_box = QtWidgets.QDoubleSpinBox()
        dspin_box.setRange(-10, 10)
        dspin_box.setPrefix("$ ")
        dspin_box.setSuffix(" Dollars")
        dspin_box.setSingleStep(0.5)
        dspin_box.valueChanged.connect(self.value_changed)
        dspin_box.textChanged.connect(self.value_changed_str)
        self.layout().addWidget(dspin_box)

        # Slider
        slider_a = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider_a.setMinimum(-10)
        slider_a.setMaximum(10)
        slider_a.setSingleStep(3)  # does not seem to be working
        slider_a.valueChanged.connect(self.value_changed_int)
        slider_a.sliderMoved.connect(self.slider_position)
        slider_a.sliderPressed.connect(self.slider_pressed)
        slider_a.sliderReleased.connect(self.slider_released)
        self.layout().addWidget(slider_a)

        # Slider Float
        slider_b = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider_b.setRange(-10, 10)
        slider_b.setSingleStep(0.01)  # does not seem to be working
        slider_b.valueChanged.connect(self.value_changed_str)
        slider_b.sliderMoved.connect(self.slider_position)
        slider_b.sliderPressed.connect(self.slider_pressed)
        slider_b.sliderReleased.connect(self.slider_released)
        self.layout().addWidget(slider_b)

        # QDial
        qdial_a = QtWidgets.QDial()
        qdial_a.setRange(-100, 100)
        qdial_a.setSingleStep(0.5)
        self.layout().addWidget(qdial_a)

        qdial_a.valueChanged.connect(self.value_changed)
        qdial_a.sliderMoved.connect(self.slider_position)
        qdial_a.sliderPressed.connect(self.slider_pressed)
        qdial_a.sliderReleased.connect(self.slider_released)

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()