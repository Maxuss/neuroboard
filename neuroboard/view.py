import sys
from PySide6.QtCore import QRect, QTimer
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QWidget,
    QLineEdit,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QDialog,
    QDialogButtonBox,
)
from p300 import capture, encode, pack


def __build_letter_widget(index: int) -> QLabel:
    label = QLabel(str(index))
    font = label.font()
    font.setPointSize(40)
    label.setFont(font)
    return label


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

        self.letters = [__build_letter_widget(i) for i in range(1, 9)]

        layout = QVBoxLayout()
        layout.addWidget(self.label1)
        layout.addSpacing(10)
        grid = QHBoxLayout()
        for letter in self.letters:
            grid.addWidget(letter)
        box = QWidget()
        box.setLayout(grid)
        layout.addWidget(box)
        layout.addSpacing(10)
        layout.addWidget(self.label2)
        layout.addWidget(self.input)
        layout.addWidget(self.button1)
        layout.addWidget(self.button2)

        container = QWidget()
        container.setLayout(layout)

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.start()

        self.setCentralWidget(container)

    def begin_capture(self):
        """Begins capture of the training data"""
        if len(self.input.text()) == 0:
            InfoDialog(
                "Введите текст тренировки",
                "Для начала тренировки введите текст, на котором будет проведено тестирование",
            ).exec_()
            return

        print("Data capture begin")
        passes = len(self.input.text())
        data = capture(
            passes,
            len(self.letters),
            lambda index: self.shift_accent(index),
        )
        self.record += 1
        print("Data capture end")
        for element in self.letters:
            element.setStyleSheet("background-color: transparent")
        encode(self.record, data, self.input.text())

    def shift_accent(self, new: int):
        """Shifts accent to the next character cell, highlighting it

        Args:
            new (int): Index of the new cell
        """
        print("Passing here")
        old = new - 1 if new != 0 else len(self.letters) - 1
        self.letters[old].setStyleSheet("background-color: transparent")
        self.letters[new].setStyleSheet("background-color: cyan")
        QApplication.processEvents()  # process events to unfreeze the application and update style sheet changes

    def save_output(self):
        """Saves the output to a gzip file"""
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
    """A dialog window with title, message and an OK button

    Args:
        QDialog (_type_): Parent dialog window type
    """

    def __init__(self, title: str, message: str):
        super().__init__()

        self.setWindowTitle(title)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(lambda: self.close())

        self.layout = QVBoxLayout()
        message = QLabel(message)
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


def show():
    """Displays this Qt application"""
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec_()
