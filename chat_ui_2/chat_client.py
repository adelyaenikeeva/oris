import sys
import socket
import threading
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit, QLineEdit, QVBoxLayout, QWidget, \
    QComboBox, QLabel
from PyQt6.QtCore import pyqtSignal, QObject, Qt
from chat_ui import ChatUI


class ChatClient(QObject):
    message_received = pyqtSignal(str)

    def __init__(self, host, port):
        super().__init__()
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))

        threading.Thread(target=self.receive_messages, daemon=True).start()

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                self.message_received.emit(message)
            except OSError as e:
                print(f"Socket error: {e}")
                break

    def send_message(self, message):
        if self.client_socket:
            self.client_socket.send(message.encode('utf-8'))

    def exit_chat(self):
        try:
            if self.client_socket:
                self.client_socket.close()
        except Exception as e:
            print(f"Error closing socket: {e}")


class ChatWindow(ChatUI):
    def __init__(self, client):
        super().__init__()
        self.client = client

        self.client.message_received.connect(self.add_message)
        self.send_button.clicked.connect(self.send_message)
        self.ban_button.clicked.connect(self.ban_user)
        self.change_room_button.clicked.connect(self.switch_window)

    def add_message(self, message):
        self.chat_text_edit.append(message)

    def send_message(self):
        message = self.message_line_edit.text()
        if message:
            self.client.send_message(message)
            self.message_line_edit.clear()

    def ban_user(self):
        self.chat_text_edit.append("Пользователь забанен!")

    def switch_window(self):
        self.hide()
        main_window.show()


class UserNameWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('АВТОРИЗАЦИЯ')
        self.setGeometry(100, 100, 400, 200)
        layout = QVBoxLayout()

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Введите ваше имя")
        layout.addWidget(self.username_input)

        self.enter_button = QPushButton("Войти", self)
        layout.addWidget(self.enter_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.enter_button.clicked.connect(self.open_main_window)

    def open_main_window(self):
        username = self.username_input.text()
        if username:
            global username_data
            username_data = username
            main_window.set_greeting(username)
            self.hide()
            main_window.show()


class MainRoomWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('ОСНОВНАЯ КОМНАТА')
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()

        self.greeting_label = QLabel(self)
        layout.addWidget(self.greeting_label)

        self.rooms_combo_box = QComboBox(self)
        self.rooms_combo_box.addItems(['room1', 'room2', 'room3'])
        layout.addWidget(self.rooms_combo_box)

        self.enter_room_button = QPushButton('Войти в комнату', self)
        layout.addWidget(self.enter_room_button)

        self.exit_button = QPushButton('Выход', self)
        layout.addWidget(self.exit_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.enter_room_button.clicked.connect(self.open_chat_window)
        self.exit_button.clicked.connect(self.exit_app)

    def set_greeting(self, username):
        self.greeting_label.setText(f"Привет, {username}!")

    def open_chat_window(self):
        self.hide()
        selected_room = self.rooms_combo_box.currentText()
        chat_window.setWindowTitle(f"КОМНАТА - {selected_room}")
        chat_window.show()

    def exit_app(self):
        self.close()
        if chat_window:
            chat_window.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    user_name_window = UserNameWindow()
    main_window = MainRoomWindow()
    client = ChatClient('localhost', 12345)
    chat_window = ChatWindow(client)

    user_name_window.show()

    sys.exit(app.exec())