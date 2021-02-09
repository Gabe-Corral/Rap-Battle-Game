import socket
import os
from _thread import *
import threading
import tkinter as tk
from text_to_speech import TextToSpeech
import vlc
import time

class Server:

    def __init__(self):
        self.ServerSideSocket = socket.socket()
        self.host = '192.168.0.108'
        self.port = 2004
        self.clients = []

        self.player_scores = {}
        self.players = []
        self.player_raps = {}
        self.player_pairs = []
        self.player_gifs = {}
        self.current_pair = 0
        self.current_pair_index = 0
        self.create_new_pairs = True
        self.round = 1
        self.vote_count = 0
        self.nickname_postion_x = 0
        self.nickname_postion_y = 0
        self.message_postion_y = 0
        self.total_rounds = 0

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
                self.send_message_to_clients(response)
            elif response.startswith("verse: "):
                self.append_new_verse(response)
            elif response.startswith("player_vote: "):
                self.handle_votes(response)
                msg_vote = response.split("player_vote: ")[1]
                self.send_message_to_clients("message: " + msg_vote + " " + "got a vote.")
            elif response.startswith("gif: "):
                res = response.split("gif: ")[1].split(" ")
                filename = res[0]
                player = res[1]
                self.set_user_gif(player, filename)

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
        self.player_scores[new_player] = 0
        self.player_raps[new_player] = []
        self.players.append(new_player)
        tk.Label(self.frame_two, text=new_player + " 5").place(
        x=self.nickname_postion_x, y=self.nickname_postion_y)
        self.nickname_postion_y += 20

    def send_message_to_clients(self, msg):
        if len(self.players) > 1:
            for client in self.clients:
                client.sendall(str.encode(msg))

    def start_game(self):
        if self.total_rounds == 3:
            self.sort_by_leaders()
            self.winner()
        else:
            self.clear_player_raps()
            self.current_pair = 0
            self.create_new_pairs = True

            if self.round == 1:
                self.start_button.destroy()

            if len(self.players) > 1:
                for client in self.clients:
                    client.sendall(str.encode("Ready!"))
            self.ready_button = tk.Button(self.root, text="Ready",
            command=self.begin_battle)
            self.ready_button.pack()

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

    def begin_battle(self):
        if self.create_new_pairs == True:
            self.ready_button.destroy()
            self.create_pairs()
            self.create_new_pair = False

        self.player_one = self.player_pairs[self.current_pair][0]
        self.player_two = self.player_pairs[self.current_pair][1]

        self.verses_label = tk.Label(self.root, text=self.player_one + " " + "VS."
        + " " + self.player_two)
        self.verses_label.pack()

        self.begin_button = tk.Button(self.root, text="Begin Battle",
        command=self.display_rap)
        self.begin_button.pack()

    def display_rap(self, player="None"):

        if player == "None":
            player = self.player_one
            self.current_player = player
            self.verses_label.destroy()
            self.begin_button.destroy()
            vote = False
        else:
            self.current_player = player
            vote = True

        self.player_label = tk.Label(self.root, text=player)
        self.player_label.pack()

        for i in self.player_raps[player]:
            label = tk.Label(self.root, text=i)
            label.pack()

        if vote:
            self.next_button = tk.Button(self.root, text="Start Vote",
            command=lambda: self.start_next_rap(next=False))
            self.next_button.pack()
        elif vote == False:
            self.next_button = tk.Button(self.root, text="Next",
            command=self.start_next_rap)
            self.next_button.pack()

        self.player_label.after(1000, self.start_rap)

    def start_rap(self):
        media = vlc.MediaPlayer("assets/beat.mp3")
        media.play()
        media.set_time(20000)
        for i in self.player_raps[self.current_player]:
            TextToSpeech(i)
        media.stop()

    def start_next_rap(self, next=True):
        children = self.root.winfo_children()
        for child in children:
            if str(child).startswith(".!label") and str(child) != ".!labelframe":
                child.destroy()
            elif str(child).startswith(".!button"):
                child.destroy()

        if next:
            self.display_rap(player=self.player_two)
        else:
            self.vote()

    def vote(self):
        vote_players = "vote: " + self.player_one + " " + self.player_two
        self.send_message_to_clients(vote_players)

    def handle_votes(self, vote):
        player_vote = vote.split("player_vote: ")[1]
        self.player_scores[player_vote] += 1
        self.vote_count += 1

        if len(self.players) == 4 and self.vote_count == len(self.players) - 2:
            self.vote_count = 0
            self.current_pair += 1
            self.round += 1
            if self.current_pair == 2:
                self.total_rounds += 1
                self.start_game()
            else:
                self.create_new_pairs = False
                self.begin_battle()

        self.update_player_scores()

    def create_pairs(self):
        if len(self.player_pairs) == 0:
            self.sort_pairs()
        else:
            self.sort_by_leaders()
            self.sort_pairs()

    def sort_pairs(self):
        index = 0
        self.player_pairs = []

        for i in range(len(self.players)):
            if i + 1 < len(self.players) and len(self.player_pairs) == 0:
                pair = (self.players[i], self.players[i+1])
                self.player_pairs.append(pair)
            elif i + 1 < len(self.players) and self.players[i] != self.player_pairs[index][1]:
                pair = (self.players[i], self.players[i+1])
                self.player_pairs.append(pair)
                index += 1
            #elif i == len(self.players)-1 and len(self.players)%2 != 0:
            #    self.player_pairs.append(self.players[i])

        print(self.player_scores, self.player_pairs )

    def sort_by_leaders(self):
        self.players = []
        self.player_scores = {key: value for key, value in sorted(self.player_scores.items(), key=lambda item: item[1])}

        for k in self.player_scores.keys():
            self.players.append(k)

    def set_user_gif(self, player, gif):
        self.player_gifs[player] = gif

    def winner(self):
        media = vlc.MediaPlayer("assets/you-win.mp3")
        media.play()
        self.winner_label = tk.Label(self.root, text="Congratulations" + " " + self.players[-1])
        self.winner_label.pack()

    def update_player_scores(self):
        children = self.frame_two.winfo_children()
        for child in children:
            player = child["text"].split(" ")[0]
            new_score = self.player_scores[player]
            child.configure(text=player + " " + str(new_score))

    def clear_player_raps(self):
        for player in self.players:
            self.player_raps[player] = []

if __name__=="__main__":
    server = Server()
