import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QAction, QMenuBar, QLabel
from PyQt5.QtGui import QLinearGradient, QColor, QBrush, QPalette, QFont
from PyQt5.QtCore import Qt, pyqtSignal

class HoverLabel(QLabel):
    clicked = pyqtSignal(int)

    def __init__(self, text, number):
        super().__init__(text)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("border: 4px solid gray; padding: 5px;")
        self.setMouseTracking(True)
        self.number = number
        font = QFont()
        font.setPointSize(20)
        self.setFont(font)

    def enterEvent(self, event):
        self.setStyleSheet("border: 4px solid Red; padding: 5px;")

    def leaveEvent(self, event):
        self.setStyleSheet("border: 4px solid gray; padding: 5px;")

    def mousePressEvent(self, event):
        self.clicked.emit(self.number)

class MenuChooser:
    def __init__(self):
        self.app = None
        self.window = None
        self.selected_number = None

    def handle_label_click(self, number):
        self.selected_number = number
        self.window.close()

    def run(self):
        self.app = QApplication(sys.argv)
        self.window = QMainWindow()
        self.window.setGeometry(100, 100, 800, 600)
        central_widget = QWidget()
        layout = QVBoxLayout()

        self.window.setWindowTitle("Remote AI")

        menubar = QMenuBar()
        file_menu = menubar.addMenu("File")
        exit_action = QAction("Exit", self.window)
        exit_action.triggered.connect(self.app.quit)
        file_menu.addAction(exit_action)
        self.window.setMenuBar(menubar)

        title_label = QLabel()
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 60px; padding: 10px;")
        title_label.setText("Remote AI")
        layout.addWidget(title_label)

        gradient = QLinearGradient(0, 0, 0, self.window.height())
        gradient.setColorAt(0, QColor(50, 100, 150))  # Start color
        gradient.setColorAt(1, QColor(150, 185, 225))  # End color

        palette = self.window.palette()
        palette.setBrush(QPalette.Background, QBrush(gradient))
        self.window.setPalette(palette)

        label1 = HoverLabel("Movement Detection", 1)
        label2 = HoverLabel("Face Detection", 2)
        label3 = HoverLabel("Object Detection", 3)
        label4 = HoverLabel("Finger Detection", 4)
        label5 = HoverLabel("Facial Expression Detection", 5)

        label1.clicked.connect(self.handle_label_click)
        label2.clicked.connect(self.handle_label_click)
        label3.clicked.connect(self.handle_label_click)
        label4.clicked.connect(self.handle_label_click)
        label5.clicked.connect(self.handle_label_click)

        layout.addWidget(label1)
        layout.addWidget(label2)
        layout.addWidget(label3)
        layout.addWidget(label4)
        layout.addWidget(label5)

        central_widget.setLayout(layout)
        self.window.setCentralWidget(central_widget)

        self.window.show()
        self.app.exec_()
        return self.selected_number

# if __name__ == '__main__':
#     label_chooser = MenuChooser()
#     chosen = label_chooser.run()
#     print(f"Selected Number: {chosen}")
