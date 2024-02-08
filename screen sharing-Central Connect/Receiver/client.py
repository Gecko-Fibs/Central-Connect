import tkinter as tk
from PIL import Image, ImageTk
from io import BytesIO
import socket
from threading import Thread
import requests

class ClientApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Screen Sharing Client")

        self.connection_code_label = tk.Label(self.master, text="Connection Code:")
        self.connection_code_label.pack()

        self.connection_code_var = tk.StringVar()
        self.connection_code_entry = tk.Entry(self.master, textvariable=self.connection_code_var)
        self.connection_code_entry.pack()

        self.start_button = tk.Button(self.master, text="Start", command=self.start_client_thread, bg="#4CAF50", fg="white")
        self.start_button.pack()

        self.label = tk.Label(self.master)
        self.label.pack()

        self.central_server_ip_response = requests.get("http://central_server_ip:5000/get_server_ip")
        self.central_server_ip = self.central_server_ip_response.json()['server_ip']

        # Listening for broadcast messages
        self.broadcast_listener_thread = Thread(target=self.listen_for_broadcast)
        self.broadcast_listener_thread.start()

    def start_client(self):
        while True:
            try:
                response = requests.get(f"http://{self.central_server_ip}:5000/get_connection_code")
                received_code = response.json()['connection_code']

                if received_code != self.connection_code_var.get():
                    print("Invalid connection code. Exiting.")
                    self.master.destroy()
                    return

                data = response.content
                img = Image.open(BytesIO(data))
                img = ImageTk.PhotoImage(img)
                self.label.configure(image=img)
                self.label.image = img
                self.master.update()  # Update the Tkinter window
            except Exception as e:
                print(f"Error: {e}")

    def start_client_thread(self):
        client_thread = Thread(target=self.start_client)
        client_thread.start()

    def listen_for_broadcast(self):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind(('0.0.0.0', 5556))
        udp_socket.settimeout(5)  # Set a timeout to avoid blocking forever

        while True:
            try:
                data, addr = udp_socket.recvfrom(1024)
                connection_code = data.decode()
                print(f"Received broadcast message: {connection_code}")
                self.connection_code_var.set(connection_code)
            except socket.timeout:
                pass

if __name__ == "__main__":
    root = tk.Tk()
    app = ClientApp(root)
    root.geometry("400x300")
    root.mainloop()
