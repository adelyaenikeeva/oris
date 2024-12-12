import socket
import threading

rooms = {
    'room1': set(),
    'room2': set(),
    'room3': set()
}

client_rooms = {}
lock = threading.Lock()


def client_handler(client_socket, client_address):
    current_room = 'room1'
    rooms[current_room].add(client_socket)
    client_rooms[client_socket] = current_room

    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if message.startswith("/switch "):
                new_room = message.split(" ")[1]
                if new_room in rooms:
                    with lock:
                        rooms[current_room].remove(client_socket)
                        current_room = new_room
                        rooms[current_room].add(client_socket)
                        client_rooms[client_socket] = current_room
                    client_socket.send(f'Switched to {new_room}'.encode('utf-8'))
                else:
                    client_socket.send('Room does not exist.'.encode('utf-8'))
            else:
                for conn in rooms[current_room]:
                    if conn != client_socket:
                        conn.send(message.encode('utf-8'))
    except:
        with lock:
            rooms[current_room].remove(client_socket)
        client_socket.close()


def start_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()

    print(f"Listening on {host}:{port}")

    while True:
        client_socket, client_address = server_socket.accept()
        threading.Thread(target=client_handler, args=(client_socket, client_address), daemon=True).start()


if __name__ == "__main__":
    start_server('localhost', 12345)