from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton
from PyQt5.QtCore import pyqtSignal, QObject
import sys


class RoomChanger(QObject):
    room_changed = pyqtSignal(str)  # Сигнал для уведомления об изменении комнаты

    def __init__(self):
        super().__init__()

    def change_room(self, room_name):
        # Здесь можно добавить логику для изменения комнаты
        print(f'Смена комнаты на: {room_name}')
        self.room_changed.emit(room_name)  # Генерируем сигнал


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Смена комнаты")

        self.room_changer = RoomChanger()

        # Соединяем сигнал с методом, который будет обрабатывать изменение комнаты
        self.room_changer.room_changed.connect(self.on_room_changed)

        # Создаём интерфейс
        self.layout = QVBoxLayout()

        self.label = QLabel("Текущая комната:")
        self.layout.addWidget(self.label)

        self.room_combo = QComboBox()
        self.room_combo.addItems(["Комната 1", "Комната 2", "Комната 3"])
        self.layout.addWidget(self.room_combo)

        self.change_room_button = QPushButton("Сменить комнату")
        self.change_room_button.clicked.connect(self.change_room)
        self.layout.addWidget(self.change_room_button)

        self.setLayout(self.layout)

    def change_room(self):
        selected_room = self.room_combo.currentText()
        self.room_changer.change_room(selected_room)

    def on_room_changed(self, room_name):
        self.label.setText(f"Текущая комната: {room_name}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())