import sys
from PySide6.QtCore import QRect
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QWidget,
    QLineEdit,
    QVBoxLayout,
    QLabel,
    QDialog,
    QDialogButtonBox,
)
from p300 import capture, encode, pack


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("NeuroBoard v0.1")
        self.setGeometry(QRect(800, 200, 800, 200))

        self.record = 0
        self.input = QLineEdit()
        self.label1 = QLabel("NeuroBoard v0.1")
        self.label2 = QLabel("Введите записываемые данные, например `1234`")
        self.button1 = QPushButton("Начать запись данных")
        self.button1.clicked.connect(self.begin_capture)
        self.button2 = QPushButton("Сохранить данные тренировки")
        self.button2.clicked.connect(self.save_output)

        layout = QVBoxLayout()
        layout.addWidget(self.label1)
        layout.addSpacing(10)
        layout.addWidget(self.label2)
        layout.addWidget(self.input)
        layout.addWidget(self.button1)
        layout.addWidget(self.button2)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

    def begin_capture(self):
        if len(self.input.text()) == 0:
            InfoDialog(
                "Введите текст тренировки",
                "Для начала тренировки введите текст, на котором будет проведено тестирование",
            ).exec_()
            return

        print("Data capture begin")
        passes = len(self.input.text())
        data = capture(++self.record, passes)
        print("Data capture end")
        encode(self.record, data, self.input.text())

    def save_output(self):
        if self.record == 0:
            InfoDialog(
                "Испытаний недостаточно",
                "Для сохранения данных проведите хотя бы одно тестирование.",
            ).exec_()
            return

        print("Saving data...")
        pack()
        print("Done saving data!")

        dlg = InfoDialog(
            "Данные сохранены",
            "Данные тренировки были сохранены в файле `nb-training.tar.gz`",
        )
        dlg.exec_()


class InfoDialog(QDialog):
    def __init__(self, title: str, message: str):
        super().__init__()

        self.setWindowTitle(title)

        QBtn = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(lambda: self.close())

        self.layout = QVBoxLayout()
        message = QLabel(message)
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


def show():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec_()
