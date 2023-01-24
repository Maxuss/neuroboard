import sys, time
from PySide2.QtCore import QRect, QTimer
from PySide2.QtWidgets import (
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
    QFormLayout,
)
from p300 import encode, pack
from requests.exceptions import ConnectionError
from config import AppConfig
from neuroplay.model.neuroplay import NeuroPlay
import time
import base64


def build_letter_widget(index: int) -> QLabel:
    label = QLabel(str(index))
    font = label.font()
    font.setPointSize(40)
    label.setFont(font)
    return label


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # TODO: actual config
        self.config = AppConfig(
            500,
            100,
            4,
            500,
        )

        self.setWindowTitle("NeuroBoard v0.1")
        self.setGeometry(QRect(800, 200, 800, 200))

        self.record = 0
        self.input = QLineEdit()
        self.label1 = QLabel("NeuroBoard v0.1")
        self.label2 = QLabel("Введите записываемые данные, например `1234`")
        self.label3 = QLabel("Набираем Символ: <>")
        font = self.label3.font()
        font.setPointSize(40)
        self.label3.setFont(font)
        self.label3.hide()
        self.button1 = QPushButton("Начать запись данных")
        self.button1.clicked.connect(self.begin_capture)
        self.button2 = QPushButton("Сохранить данные тренировки")
        self.button2.clicked.connect(self.save_output)
        self.button3 = QPushButton("Настройки")
        self.button3.clicked.connect(lambda: SettingsWindow(self.config).exec_())

        self.letters = [build_letter_widget(i) for i in range(0, 10)]

        layout = QVBoxLayout()
        layout.addWidget(self.label1)
        layout.addSpacing(10)
        grid = QHBoxLayout()
        grid.addWidget(self.label3)
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
        layout.addWidget(self.button3)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

    def do_capture(self, element_count: int) -> bytes:
        """Captures data from the NeuroPlay device

        Returns:
            bytes: Recorded bytes
        """

        play = NeuroPlay()
        play.set_connected(True)
        # play.enable_data_grab()
        play.start_record()
        for element in range(0, element_count):
            for letter in self.letters:
                letter.hide()
            self.label3.setText(f"Набираем Символ {self.letters[element].text()}")
            self.label3.show()
            QApplication.processEvents()

            time.sleep(self.config.delay_time / 1000.0)

            self.show_letters()
            QApplication.processEvents()

            for j in range(0, self.config.pass_count):
                for i in range(0, element_count):
                    ## highlighting the element
                    self.letters[i].setStyleSheet("background-color: cyan")
                    QApplication.processEvents()
                    ## waiting for highlight time
                    time.sleep(self.config.highlight_time_ms / 1000.0)
                    ## making the element transparent again
                    self.letters[i].setStyleSheet("background-color: transparent")
                    QApplication.processEvents()
                    ## waiting for delay time
                    time.sleep(
                        (self.config.cycle_time_ms - self.config.highlight_time_ms)
                        / 1000.0
                    )
                    # print(f"recording element {element} pass {i}")
                    play.add_edf_annotation(f"i_{element}$p_{j}$c_{i}")
        data = play.stop_record()
        if data.ok:
            response = data.json()
            print(response)
            return base64.b64decode(response["files"][0]["data"])
        return ""

    def show_letters(self):
        self.label3.hide()
        for letter in self.letters:
            letter.show()

    def begin_capture(self):
        """Begins capture of the training data"""
        if len(self.input.text()) == 0:
            InfoDialog(
                "Введите текст тренировки",
                "Для начала тренировки введите текст, на котором будет проведено тестирование",
            ).exec_()
            return

        try:
            # print("Data capture begin")
            data = self.do_capture(len(self.letters))
            self.record += 1
            # print("Data capture end")
            # for element in self.letters:
            #     element.setStyleSheet("background-color: transparent")
            encode(self.record, data, self.input.text())

        except ConnectionError:
            InfoDialog(
                "Не удалось подключиться к серверу",
                "Для записи данных необходимо запустить программу NeuroPlay",
            ).exec_()

    def save_output(self):
        """Saves the output to a gzip file"""
        if self.record == 0:
            InfoDialog(
                "Испытаний недостаточно",
                "Для сохранения данных проведите хотя бы одно тестирование.",
            ).exec_()
            return

        # print("Saving data...")
        pack()
        # print("Done saving data!")

        dlg = InfoDialog(
            "Данные сохранены",
            "Данные тренировки были сохранены в файле `nb-training.tar.gz`",
        )
        dlg.exec_()


class SettingsWindow(QDialog):
    """A settings dialog window

    Args:
        QDialog (_type_): Parent dialog window type
    """

    def __init__(self, current_config: AppConfig) -> None:
        super().__init__()

        self.setWindowTitle("Настройки")

        self.config = current_config

        layout = QVBoxLayout()
        self.form = QFormLayout()
        self.cycle_time = QLineEdit(str(current_config.cycle_time_ms))
        self.highlight_time = QLineEdit(str(current_config.highlight_time_ms))
        self.pass_count = QLineEdit(str(current_config.pass_count))
        self.delay_time = QLineEdit(str(current_config.delay_time))

        self.form.addRow("Время цикла (Миллисекунды):", self.cycle_time)
        self.form.addRow("Время подсветки (Миллисекунды):", self.highlight_time)
        self.form.addRow("Количество повторов на символ:", self.pass_count)
        self.form.addRow("Задержка между повторами (Миллисекуенды):", self.delay_time)

        layout.addLayout(self.form)
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.save)
        layout.addWidget(self.buttonBox)

        self.setLayout(layout)

    def save(self):
        cycle_time: QLineEdit = self.cycle_time.text()
        highlight_time: QLineEdit = self.highlight_time.text()
        passes: QLineEdit = self.pass_count.text()
        delay_time: QLineEdit = self.delay_time.text()

        self.config.cycle_time_ms = int(cycle_time)
        self.config.highlight_time_ms = int(highlight_time)
        self.config.pass_count = int(passes)
        self.config.delay_time = int(delay_time)

        self.close()


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
