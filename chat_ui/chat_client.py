import sys
import socket
import threading
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import pyqtSignal, QObject
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
        self.exit_button.clicked.connect(self.exit_chat)

        # self.rooms_combo_box.currentTextChanged.connect(self.change_room)

    def add_message(self, message):
        self.chat_text_edit.append(message)

    def send_message(self):
        message = self.message_line_edit.text()
        self.client.send_message(message)
        self.message_line_edit.clear()

    # def change_room(self, room_name):
    #     self.client.switch_room(room_name)
    #
    # def switch_room(self, room_name):
    #     self.send_message(f"/switch {room_name}")

    def ban_user(self):
        self.chat_text_edit.append("Пользователь забанен!")

    def exit_chat(self):
        self.client.exit_chat()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = ChatClient('localhost', 12345)
    window = ChatWindow(client)
    window.show()
    app.exec()