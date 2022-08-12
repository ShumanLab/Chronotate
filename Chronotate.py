# Chronotate Author Paul A. Philipsberg
# https://github.com/pphilipsberg



# tkVideoPlayer and sample player Author Paul (PaulleDemon)
# https://github.com/PaulleDemon

# MIT License
#
# Copyright (c) 2021 Paul
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import os
import datetime
import tkinter as tk
from tkinter import filedialog
from tkVideoPlayer import TkinterVideo  # this version of tkVideoPlayer is a modified version based off release 2.2
import pandas as pd


class chronotate:

    def __init__(self):

        self.object_1_key = "j"
        self.object_2_key = "k"
        self.object_3_key = "l"
        self.object_4_key = "semicolon"

        self.key1_down = False
        self.key2_down = False
        self.key3_down = False
        self.key4_down = False

        # self.object_1_starts = []
        # self.object_2_starts = []
        # self.object_3_starts = []
        # self.object_4_starts = []
        #
        # self.object_1_ends = []
        # self.object_2_ends = []
        # self.object_3_ends = []
        # self.object_4_ends = []

        self.marker_time = []
        self.marker_type = []
        self.object_id = []

        self.root = tk.Tk()
        self.root.title("chronoNotate")
        self.root.geometry("800x720")

        # frame = tk.Frame(root, width=100, height=100)
        # frame.bind("<KeyPress>", keydown)
        # frame.bind("<KeyRelease>", keyup)
        # frame.pack()
        # frame.focus_set()

        self.root.bind("<KeyPress>", self.keydown)  # lambda event, arg=self.keysNum: self.keydown(event, arg))
        self.root.bind("<KeyRelease>", self.keyup)

        self.load_video_btn = tk.Button(self.root, text="Load Video", command=self.load_video)
        self.load_video_btn.pack()
        self.load_markers_btn = tk.Button(self.root, text="Load Marker File", command=self.load_markers)
        self.load_markers_btn.pack()

        self.clr_markers_btn = tk.Button(self.root, text="Clear Markers", command=self.clear_markers)

        self.vid_frame = tk.Frame(self.root)
        self.btn_frame = tk.Frame(self.root)
        self.vid_player = TkinterVideo(scaled=True, consistant_frame_rate=True, master=self.vid_frame)
        self.vid_player.pack(side="left", expand=True, fill="both")

        self.list_box = tk.Listbox(self.vid_frame)
        self.list_box.pack(side="left", fill="y")
        self.scroll_bar = tk.Scrollbar(self.vid_frame)
        self.scroll_bar.pack(side="right", fill="y")
        self.list_box.config(yscrollcommand=self.scroll_bar.set)
        self.scroll_bar.config(command=self.list_box.yview)

        self.list_box.bind('<<ListboxSelect>>', self.select_marker)

        self.vid_frame.pack(expand=True, fill="both")
        self.btn_frame.pack(expand=False, fill="x")


        self.skip_plus_5sec = tk.Button(self.btn_frame, text="Skip -5 sec", command=lambda: self.skip(-5))
        self.skip_plus_5sec.pack(side="left")

        self.start_time = tk.Label(self.btn_frame, text=str(datetime.timedelta(seconds=0)))
        self.start_time.pack(side="left")

        self.progress_value = tk.IntVar(self.root)

        # self.progress_slider = tk.Scale(self.btn_frame, variable=self.progress_value, from_=0, to=0, orient="horizontal", command=self.seek)
        self.progress_slider = tk.Scale(self.btn_frame, variable=self.progress_value, from_=0, to=0, orient="horizontal", command=self.seek)
        self.progress_slider.pack(side="left", fill="x", expand=True)

        self.end_time = tk.Label(self.btn_frame, text=str(datetime.timedelta(seconds=0)))
        self.end_time.pack(side="left")

        self.skip_plus_5sec = tk.Button(self.btn_frame, text="Skip +5 sec", command=lambda: self.skip(5))
        self.skip_plus_5sec.pack(side="left")

        self.play_pause_btn = tk.Button(self.root, text="Play", command=self.play_pause)
        self.play_pause_btn.pack()

        self.speed_var = tk.DoubleVar()
        self.speed_var.set(1)

        self.speed_frame = tk.Frame(self.root)

        options = [
            .125,
            .25,
            .5,
            1,
            2,
            4,
            8
        ]

        self.speed_lbl = tk.Label(self.speed_frame, text='playback speed')
        self.speed_lbl.pack(side="left")
        self.speed_menu = tk.OptionMenu(self.speed_frame, self.speed_var, *options, command=self.play_speed)
        self.speed_menu.pack(side="right")
        self.speed_frame.pack()

        self.export_btn = tk.Button(self.root, text="export", command=self.export)
        self.export_btn.pack()

        self.vid_player.bind("<<Duration>>", self.update_duration)
        self.vid_player.bind("<<SecondChanged>>", self.update_scale)
        self.vid_player.bind("<<Ended>>", self.video_ended)

        self.root.mainloop()

    def keyup(self, event):
        if event.keysym == self.object_1_key:
            self.key1_down = False
            # self.object_1_ends = self.object_1_ends + [self.vid_player.current_duration()]
            # print(self.object_1_ends)
            # self.marker_time = self.marker_time + [self.vid_player.current_duration()]
            # self.marker_type = self.marker_type + ["stop"]
            # self.object_id = self.object_id + [1]

            self.add_marker("stop", 1)

        elif event.keysym == self.object_2_key:
            self.key2_down = False
            # self.object_2_ends = self.object_2_ends + [self.vid_player.current_duration()]
            # print(self.object_2_ends)
            # self.marker_time = self.marker_time + [self.vid_player.current_duration()]
            # self.marker_type = self.marker_type + ["stop"]
            # self.object_id = self.object_id + [2]
            self.add_marker("stop", 2)

        elif event.keysym == self.object_3_key:
            self.key3_down = False
            # self.object_3_ends = self.object_3_ends + [self.vid_player.current_duration()]
            # print(self.object_3_ends)
            # self.marker_time = self.marker_time + [self.vid_player.current_duration()]
            # self.marker_type = self.marker_type + ["stop"]
            # self.object_id = self.object_id + [3]
            self.add_marker("stop", 3)

        elif event.keysym == self.object_4_key:
            self.key4_down = False
            # self.object_4_ends = self.object_4_ends + [self.vid_player.current_duration()]
            # print(self.object_4_ends)
            # self.marker_time = self.marker_time + [self.vid_player.current_duration()]
            # self.marker_type = self.marker_type + ["stop"]
            # self.object_id = self.object_id + [4]
            self.add_marker("stop", 4)

    def keydown(self, event):  # , arg):
        if (event.keysym == self.object_1_key) & (~self.key1_down):
            self.key1_down = True
            # self.object_1_starts = self.object_1_starts + [self.vid_player.current_duration()]
            # print(self.object_1_starts)
            # self.marker_time = self.marker_time + [self.vid_player.current_duration()]
            # self.marker_type = self.marker_type + ["start"]
            # self.object_id = self.object_id + [1]
            self.add_marker("start", 1)

        elif (event.keysym == self.object_2_key) & (~self.key2_down):
            self.key2_down = True
            # self.object_2_starts = self.object_2_starts + [self.vid_player.current_duration()]
            # print(self.object_2_starts)
            # self.marker_time = self.marker_time + [self.vid_player.current_duration()]
            # self.marker_type = self.marker_type + ["start"]
            # self.object_id = self.object_id + [2]
            self.add_marker("start", 2)

        elif (event.keysym == self.object_3_key) & (~self.key3_down):
            self.key3_down = True
            # self.object_3_starts = self.object_3_starts + [self.vid_player.current_duration()]
            # print(self.object_3_starts)
            # self.marker_time = self.marker_time + [self.vid_player.current_duration()]
            # self.marker_type = self.marker_type + ["start"]
            # self.object_id = self.object_id + [3]
            self.add_marker("start", 3)

        elif (event.keysym == self.object_4_key) & (~self.key4_down):
            self.key4_down = True
            # self.object_4_starts = self.object_4_starts + [self.vid_player.current_duration()]
            # print(self.object_4_starts)
            # self.marker_time = self.marker_time + [self.vid_player.current_duration()]
            # self.marker_type = self.marker_type + ["start"]
            # self.object_id = self.object_id + [4]
            self.add_marker("start", 4)

    def update_duration(self, event):
        """ updates the duration after finding the duration """
        self.vid_player.duration = self.vid_player.video_info()["duration"]
        self.end_time["text"] = str(datetime.timedelta(seconds=self.vid_player.duration))
        self.progress_slider["to"] = self.vid_player.duration

    def update_scale(self, event):
        """ updates the scale value """
        #self.progress_slider.set(self.vid_player.current_duration())
        self.progress_value.set(self.vid_player.current_duration())

    def load_video(self):
        """ loads the video """
        self.clear_markers()
        self.video_file_path = filedialog.askopenfilename(title='select')

        if self.video_file_path:
            self.vid_player.load(self.video_file_path)
            # print(self.vid_player.video_info()["duration"])
            self.progress_slider.config(to=0, from_=0)
            #self.progress_slider.set(0)
            self.progress_value.set(0)
            self.play_pause_btn["text"] = "Play"

    def load_markers(self):
        self.clear_markers()
        marker_file_path = filedialog.askopenfilename(title='select', filetypes=[("csv files", ".csv")])
        df = pd.read_csv(marker_file_path)
        self.marker_time = df['marker_time'].tolist()
        self.marker_type = df['marker_type'].tolist()
        self.object_id = df['object_id'].tolist()

        for x in range(0,len(self.marker_time)):
            mkrId = self.object_id[x]
            mkrType = self.marker_type[x]
            time_now = self.marker_time[x]
            self.list_box.insert(tk.END, 'object %s %s: %ss' % (mkrId, mkrType, time_now))

    def seek(self, value):
        """ used to seek a specific timeframe """
        # print('target time')
        #print(float(value))
        self.vid_player.seek(float(value))
        #print(self.vid_player.current_duration())

    def skip(self, value: int):
        """ skip seconds """
        # print('target time')
        #print(float(self.progress_value.get()+value))
        # print(self.vid_player.current_duration()+value)

        #self.vid_player.current_duration()
        # self.vid_player.seek(self.progress_value.get()+value)
        #self.progress_value.set(self.progress_value.get() + value)

        self.vid_player.seek(self.vid_player.current_duration()+value)
        #self.progress_value.set(self.vid_player.current_duration() + value)

    def play_pause(self):
        """ pauses and plays """
        if self.vid_player.is_paused():
            self.vid_player.play()
            self.play_pause_btn["text"] = "Pause"

        else:
            self.vid_player.pause()
            self.play_pause_btn["text"] = "Play"

    def play_speed(self, event):
        # print(self.speed_var.get())
        self.vid_player.set_speed(self.speed_var.get())

    def export(self):
        # df = pd.DataFrame(
        #     {'object_1_starts': self.object_1_starts,
        #      'object_1_ends': self.object_1_ends,
        #      'object_2_starts': self.object_2_starts,
        #      'object_2_ends': self.object_2_ends,
        #      'object_3_starts': self.object_3_starts,
        #      'object_3_ends': self.object_3_ends,
        #      'object_4_starts': self.object_4_starts,
        #      'object_4_ends': self.object_4_ends})
        df = pd.DataFrame(
            {'marker_time': self.marker_time,
             'marker_type': self.marker_type,
             'object_id': self.object_id})

        export_path = os.path.splitext(self.video_file_path)[0] + '_markers.csv'
        df.to_csv(export_path, index=False)

    def video_ended(self, event):
        """ handle video ended """
        self.progress_slider.set(self.progress_slider["to"])
        self.play_pause_btn["text"] = "Play"
        self.progress_slider.set(0)

    def add_marker(self, mkrType, mkrId):
        time_now = self.vid_player.current_duration()
        self.marker_time = self.marker_time + [time_now]
        self.marker_type = self.marker_type + [mkrType]
        self.object_id = self.object_id + [mkrId]
        self.list_box.insert(tk.END, 'object %s %s: %ss' % (mkrId, mkrType, time_now))
        self.list_box.yview(tk.END)

    def clear_markers(self):
        self.list_box.delete(0, tk.END)
        self.marker_time = []
        self.marker_type = []
        self.object_id = []

    def select_marker(self, event):
        w = event.widget
        index = int(w.curselection()[0])
        select_time = self.marker_time[index]
        self.seek(select_time)
        self.progress_value.set(select_time)



app = chronotate()


