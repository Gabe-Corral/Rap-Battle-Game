import socket
import os
from _thread import *
import threading
import tkinter as tk

class Server:

    def __init__(self):
        self.ServerSideSocket = socket.socket()
        self.host = '127.0.0.1'
        self.port = 2004
        self.clients = []

        self.players = {}
        self.player_raps = {}
        self.nickname_postion_x = 0
        self.nickname_postion_y = 0
        self.message_postion_y = 0

        self.thread_one = threading.Thread(target=self.start_gui)
        self.thread_one.start()

        self.bind_server_socket()
        self.start_main_loop()

    def start_gui(self):
        self.root = tk.Tk()
        self.root.wm_title("Rap Game Server")
        self.root.geometry("900x900")

        #labelframe/canvas for joining players
        self.wrapper_two = tk.LabelFrame(self.root)
        self.canvas_two = tk.Canvas(self.wrapper_two, height=100, width=900)
        self.frame_two = tk.Frame(self.canvas_two)
        self.canvas_two.pack(side=tk.LEFT, fill="x")
        self.canvas_two.create_window((0, 0), window=self.frame_two, anchor="nw",
        height=100, width=900)
        self.wrapper_two.pack(fill="x", side="top")

        self.title = tk.Label(self.root, text="Epic Rap Battles Of Orbs")
        self.title.configure(font="25")
        self.title.pack(padx=5, pady=5)
        self.start_button = tk.Button(self.root, text="Start",
        width=10, command=self.start_game)
        self.start_button.pack()

        tk.mainloop()

    def bind_server_socket(self):
        self.ThreadCount = 0
        try:
            self.ServerSideSocket.bind((self.host, self.port))
        except socket.error as e:
            print(str(e))

        print('Socket is listening..')
        self.ServerSideSocket.listen(5)

    def multi_threaded_client(self, connection):
        self.connection = connection
        connection.send(str.encode('Server is working:'))
        while True:

            data = connection.recv(2048)
            response = data.decode('utf-8')

            if not data:
                break

            connection.sendall(str.encode(response))

            print(response)

            if response.startswith("nickname: "):
                self.add_player(response)
            elif response.startswith("message: "):
                self.display_message(response, connection)
            elif response.startswith("verse: "):
                self.append_new_verse(response)

        connection.close()

    def start_main_loop(self):
        while True:
            Client, address = self.ServerSideSocket.accept()
            self.clients.append(Client)
            print('Connected to: ' + address[0] + ':' + str(address[1]))
            start_new_thread(self.multi_threaded_client, (Client, ))
            self.ThreadCount += 1
            print('Thread Number: ' + str(self.ThreadCount))
        self.ServerSideSocket.close()

    def add_player(self, player):
        new_player = player.split("nickname: ")[1]
        self.players[new_player] = 5
        self.player_raps[new_player] = []
        tk.Label(self.frame_two, text=new_player).place(
        x=self.nickname_postion_x, y=self.nickname_postion_y)
        self.nickname_postion_y += 20

    def display_message(self, msg, connection):
        if len(self.players) > 1:
            for client in self.clients:
                client.sendall(str.encode(msg))

    def start_game(self):
        if len(self.players) > 1:
            for client in self.clients:
                client.sendall(str.encode("Ready!"))

    def message_clients(self, connection):
        message = input("message: ")
        connection.send(message.encode())
        connection.recv(1024)

    def append_new_verse(self, verse):
        new_verse = verse.split("verse: ")[1]
        verse_arr = new_verse.split(" ")
        player_name = verse_arr[0]
        verse_arr.pop(0)
        new_verse = " ".join(verse_arr)
        self.player_raps[player_name].append(new_verse)


if __name__=="__main__":
    server = Server()
