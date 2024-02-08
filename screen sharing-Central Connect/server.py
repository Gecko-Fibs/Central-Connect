import tkinter as tk
from threading import Thread
from flask import Flask, jsonify
import socket
from PIL import ImageGrab, ImageTk, Image
from io import BytesIO
import requests
import os

app = Flask(__name__)
server_socket = None

def send_screen(client_socket):
    while True:
        screenshot = ImageGrab.grab()
        buffered = BytesIO()
        screenshot.save(buffered, format="PNG")
        data = buffered.getvalue()
        client_socket.send(data)

@app.route('/get_connection_code', methods=['POST'])
def get_connection_code():
    connection_code = generate_connection_code()
    return jsonify({'connection_code': connection_code})

class ServerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Screen Sharing Server")

        self.connection_code_label = tk.Label(self.master, text="Connection Code:")
        self.connection_code_label.pack()

        self.connection_code_var = tk.StringVar()
        self.connection_code_entry = tk.Entry(self.master, textvariable=self.connection_code_var, state='readonly')
        self.connection_code_entry.pack()

        self.generate_code_button = tk.Button(self.master, text="Generate Code", command=self.generate_connection_code)
        self.generate_code_button.pack(pady=10)

        self.start_server_button = tk.Button(master, text="Start Server", command=self.start_server_and_flask, bg="#4CAF50", fg="white")
        self.start_server_button.pack(pady=20)

    def generate_connection_code(self):
        response = requests.post("http://central_server_ip:5000/get_connection_code")
        connection_code = response.json()['connection_code']
        self.connection_code_var.set(connection_code)

    def start_server_and_flask(self):
        start_server_and_flask(self.connection_code_var.get())
        self.broadcast_connection_code()
        self.start_server_button.config(state=tk.DISABLED)
        self.master.after(1000, self.check_server_status)

    def broadcast_connection_code(self):
        server_ip_response = requests.get("http://central_server_ip:5000/get_server_ip")
        server_ip = server_ip_response.json()['server_ip']
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.sendto(self.connection_code_var.get().encode(), (server_ip, 5556))
        udp_socket.close()

    def check_server_status(self):
        if server_socket and server_socket.fileno() != -1:
            self.master.after(1000, self.check_server_status)
        else:
            self.start_server_button.config(state=tk.NORMAL)

def generate_connection_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

def start_server_and_flask(connection_code):
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 5555))

    print("Server is starting...")

    server_socket.listen(1)
    print("Server is listening on port 5555")

    client_socket, addr = server_socket.accept()
    print(f"Connection from {addr}")

    send_screen_thread = Thread(target=send_screen, args=(client_socket,))
    send_screen_thread.start()

    # Run Flask app in a separate thread
    flask_thread = Thread(target=start_flask, args=(connection_code,))
    flask_thread.start()

def start_flask(connection_code):
    app.run(port=5000, extra_files={'/': connection_code})

if __name__ == "__main__":
    root = tk.Tk()
    app = ServerApp(root)
    root.geometry("400x200")
    root.mainloop()
