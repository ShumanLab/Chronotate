# Chronotate Author Paul A. Philipsberg
# https://github.com/pphilipsberg



# tkVideoPlayer and sample player Author Paul (PaulleDemon)
# https://github.com/PaulleDemon

# MIT License
#
# Copyright (c) 2022 Paul
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
import json
# import sys
# import time
import tkinter as tk
from tkinter import filedialog
from tkVideoPlayer import TkinterVideo  # this version of tkVideoPlayer is a modified version based off release 2.2
import pandas as pd
# from PIL import ImageTk, Image, ImageOps


class chronotate:

    def __init__(self):

        self.keysDict_default = {
        "object_1_key" : 74,  # "j"
        "object_2_key" : 75,  # "k"
        "object_3_key" : 76,  # "l"
        "object_4_key" : 186,  # "semicolon"

        "speed_up_key" : 87,  # 'w'
        "speed_down_key" : 83,  # 's'
        "skip_back_key" : 65,  # 'a'
        "skip_forward_key" : 68,  # 'd'
        "play_key" : 32  # 'space'
        }

        self.keySymDict_default = {
        "object_1_key" : "j",
        "object_2_key" : "k",
        "object_3_key" : "l",
        "object_4_key" : "semicolon",

        "speed_up_key" : 'w',
        "speed_down_key" : 's',
        "skip_back_key" : 'a',
        "skip_forward_key" : 'd',
        "play_key" : 'space'
        }

        keyBindsFile = os.path.join(os.getcwd(), 'keyBinds.json')

        if os.path.isfile(keyBindsFile):
            with open(keyBindsFile, 'r') as fd:
                keysDictList = json.load(fd)
                self.keySymDict = keysDictList[0]
                self.keysDict = keysDictList[1]
        else:
            self.keySymDict = self.keySymDict_default
            self.keysDict = self.keysDict_default





        self.object_1_key = 74  # "j"
        self.object_2_key = 75  # "k"
        self.object_3_key = 76  # "l"
        self.object_4_key = 186  # "semicolon"

        self.speed_up_key = 87  # 'w'
        self.speed_down_key = 83  # 's'
        self.skip_back_key = 65  # 'a'
        self.skip_forward_key = 68  # 'd'
        self.play_key = 32  # 'space'

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


        self.root.title("Chronotate")
        # self.root.iconbitmap("Chronotate.ico")
        self.root.geometry("800x720")

        # frame = tk.Frame(root, width=100, height=100)
        # frame.bind("<KeyPress>", keydown)
        # frame.bind("<KeyRelease>", keyup)
        # frame.pack()
        # frame.focus_set()

        self.root.unbind_class("Listbox", "<Key-space>")

        self.root.bind("<KeyPress>", self.keydown)  # lambda event, arg=self.keysNum: self.keydown(event, arg))
        self.root.bind("<KeyRelease>", self.keyup)

#######################################################################################################################
        self.bindKeysButton = tk.Button(self.root, text="customize key binds", command=self.popup)
        self.bindKeysButton.pack()
#######################################################################################################################

        self.load_video_frame = tk.Frame(self.root)
        self.load_video_btn = tk.Button(self.load_video_frame, text="Load Video", command=self.load_video)
        self.load_video_btn.pack(side='left')
        self.video_file_path = ''
        self.loaded_video = tk.Label(self.load_video_frame, text=self.video_file_path)
        self.loaded_video.pack(side='left')
        self.load_video_frame.pack()

        self.load_markers_frame = tk.Frame(self.root)
        self.load_markers_btn = tk.Button(self.load_markers_frame, text="Load Marker File", command=self.load_markers)
        self.load_markers_btn.pack(side='left')
        self.marker_file_path = ''
        self.loaded_marker_file = tk.Label(self.load_markers_frame, text=self.marker_file_path)
        self.loaded_marker_file.pack(side='left')
        self.load_markers_frame.pack()

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

        self.progress_value = tk.DoubleVar(self.root)

        # self.progress_slider = tk.Scale(self.btn_frame, variable=self.progress_value, from_=0, to=0, orient="horizontal", command=self.seek)
        self.progress_slider = tk.Scale(self.btn_frame, variable=self.progress_value, resolution=0.1, from_=0, to=0, orient="horizontal", command=self.seek)
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
        # self.vid_player.bind("<<SecondChanged>>", self.update_scale)
        self.vid_player.bind("<<Update>>", self.update_scale)  # update scale evey frame
        self.vid_player.bind("<<Ended>>", self.video_ended)



        self.root.mainloop()

    def popup(self):
        self.keyBindPopup=keyBindWindow(self.root, self)

        for child in self.root.winfo_children():
            try:
                child.configure(state='disable')
            except:
                pass
            if child.winfo_class() == 'Frame':
                for grandChild in child.winfo_children():
                    try:
                        grandChild.configure(state='disable')
                    except:
                        pass

        self.root.wait_window(self.keyBindPopup.top)

        for child in self.root.winfo_children():
            try:
                child.configure(state='normal')
            except:
                pass
            if child.winfo_class() == 'Frame':
                for grandChild in child.winfo_children():
                    try:
                        grandChild.configure(state='normal')
                    except:
                        pass

    def entryValue(self):
        return self.keyBindPopup.value

    def keyup(self, event):
        if event.keycode == self.keysDict["object_1_key"]:
            self.key1_down = False
            # self.object_1_ends = self.object_1_ends + [self.vid_player.current_duration()]
            # print(self.object_1_ends)
            # self.marker_time = self.marker_time + [self.vid_player.current_duration()]
            # self.marker_type = self.marker_type + ["stop"]
            # self.object_id = self.object_id + [1]

            self.add_marker("stop", 1)

        elif event.keycode == self.keysDict["object_2_key"]:
            self.key2_down = False
            # self.object_2_ends = self.object_2_ends + [self.vid_player.current_duration()]
            # print(self.object_2_ends)
            # self.marker_time = self.marker_time + [self.vid_player.current_duration()]
            # self.marker_type = self.marker_type + ["stop"]
            # self.object_id = self.object_id + [2]
            self.add_marker("stop", 2)

        elif event.keycode == self.keysDict["object_3_key"]:
            self.key3_down = False
            # self.object_3_ends = self.object_3_ends + [self.vid_player.current_duration()]
            # print(self.object_3_ends)
            # self.marker_time = self.marker_time + [self.vid_player.current_duration()]
            # self.marker_type = self.marker_type + ["stop"]
            # self.object_id = self.object_id + [3]
            self.add_marker("stop", 3)

        elif event.keycode == self.keysDict["object_4_key"]:
            self.key4_down = False
            # self.object_4_ends = self.object_4_ends + [self.vid_player.current_duration()]
            # print(self.object_4_ends)
            # self.marker_time = self.marker_time + [self.vid_player.current_duration()]
            # self.marker_type = self.marker_type + ["stop"]
            # self.object_id = self.object_id + [4]
            self.add_marker("stop", 4)

    def keydown(self, event):  # , arg):
        # print(event.keycode)
        if (event.keycode == self.keysDict["object_1_key"]) & (~self.key1_down):
            self.key1_down = True
            # self.object_1_starts = self.object_1_starts + [self.vid_player.current_duration()]
            # print(self.object_1_starts)
            # self.marker_time = self.marker_time + [self.vid_player.current_duration()]
            # self.marker_type = self.marker_type + ["start"]
            # self.object_id = self.object_id + [1]
            self.add_marker("start", 1)

        elif (event.keycode == self.keysDict["object_2_key"]) & (~self.key2_down):
            self.key2_down = True
            # self.object_2_starts = self.object_2_starts + [self.vid_player.current_duration()]
            # print(self.object_2_starts)
            # self.marker_time = self.marker_time + [self.vid_player.current_duration()]
            # self.marker_type = self.marker_type + ["start"]
            # self.object_id = self.object_id + [2]
            self.add_marker("start", 2)

        elif (event.keycode == self.keysDict["object_3_key"]) & (~self.key3_down):
            self.key3_down = True
            # self.object_3_starts = self.object_3_starts + [self.vid_player.current_duration()]
            # print(self.object_3_starts)
            # self.marker_time = self.marker_time + [self.vid_player.current_duration()]
            # self.marker_type = self.marker_type + ["start"]
            # self.object_id = self.object_id + [3]
            self.add_marker("start", 3)

        elif (event.keycode == self.keysDict["object_4_key"]) & (~self.key4_down):
            self.key4_down = True
            # self.object_4_starts = self.object_4_starts + [self.vid_player.current_duration()]
            # print(self.object_4_starts)
            # self.marker_time = self.marker_time + [self.vid_player.current_duration()]
            # self.marker_type = self.marker_type + ["start"]
            # self.object_id = self.object_id + [4]
            self.add_marker("start", 4)

        elif event.keycode == self.keysDict["speed_up_key"]:
            self.speed_var.set(min(max(self.speed_var.get()*2, .125), 8))
            self.vid_player.set_speed(self.speed_var.get())

        elif event.keycode == self.keysDict["speed_down_key"]:
            self.speed_var.set(min(max(self.speed_var.get()/2, .125), 8))
            self.vid_player.set_speed(self.speed_var.get())

        elif event.keycode == self.keysDict["skip_back_key"]:
            self.skip(-5)

        elif event.keycode == self.keysDict["skip_forward_key"]:
            self.skip(5)

        elif event.keycode == self.keysDict["play_key"]:
            self.play_pause()


    def update_duration(self, event):
        """ updates the duration after finding the duration """
        self.vid_player.duration = self.vid_player.video_info()["duration"]
        self.end_time["text"] = str(datetime.timedelta(seconds=self.vid_player.duration))
        self.progress_slider["to"] = self.vid_player.duration

    def update_scale(self, event):
        """ updates the scale value """
        # print(self.vid_player.current_duration())
        self.progress_value.set(self.vid_player.current_duration())

    def load_video(self):
        """ loads the video """
        self.clear_markers()
        self.video_file_path = filedialog.askopenfilename(title='select')

        if self.video_file_path:
            self.loaded_video["text"] = self.video_file_path
            self.vid_player.load(self.video_file_path)
            # print(self.vid_player.video_info()["duration"])
            self.progress_slider.config(to=0, from_=0)
            #self.progress_slider.set(0)
            self.progress_value.set(0)
            self.play_pause_btn["text"] = "Play"
            # self.vid_player._display_frame()
            # self.vid_player.current_imgtk = ImageTk.PhotoImage(self.vid_player.current_img)

    def load_markers(self):
        self.clear_markers()
        self.marker_file_path = filedialog.askopenfilename(title='select', filetypes=[("csv files", ".csv")])
        self.loaded_marker_file["text"] = self.marker_file_path
        df = pd.read_csv(self.marker_file_path)
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

class keyBindWindow:
    def __init__(self, master, callingInstance):
        self.master = master
        top = self.top = tk.Toplevel(master)
        self.top.bind("<KeyPress>", self.bindKey)
        self.callingInstance = callingInstance

        # self.skip_plus_5sec = tk.Button(self.btn_frame, text="Skip +5 sec", command=lambda: self.skip(5))
        self.bindObject1 = tk.Button(top, text="Bind Object 1 key", command=lambda: self.bindAction("object_1_key", self.Object1Label))
        self.bindObject1.pack()
        self.Object1Label = tk.Label(top, text=self.callingInstance.keySymDict["object_1_key"])
        self.Object1Label.pack()

        self.bindObject2 = tk.Button(top, text="Bind Object 2 key", command=lambda: self.bindAction("object_2_key", self.Object2Label))
        self.bindObject2.pack()
        self.Object2Label = tk.Label(top, text=self.callingInstance.keySymDict["object_2_key"])
        self.Object2Label.pack()

        self.bindObject3 = tk.Button(top, text="Bind Object 3 key", command=lambda: self.bindAction("object_3_key", self.Object3Label))
        self.bindObject3.pack()
        self.Object3Label = tk.Label(top, text=self.callingInstance.keySymDict["object_3_key"])
        self.Object3Label.pack()

        self.bindObject4 = tk.Button(top, text="Bind Object 4 key", command=lambda: self.bindAction("object_4_key", self.Object4Label))
        self.bindObject4.pack()
        self.Object4Label = tk.Label(top, text=self.callingInstance.keySymDict["object_4_key"])
        self.Object4Label.pack()

        self.bindSpeedUp = tk.Button(top, text="Bind speed up key", command=lambda: self.bindAction("speed_up_key", self.SpeedUpLabel))
        self.bindSpeedUp.pack()
        self.SpeedUpLabel = tk.Label(top, text=self.callingInstance.keySymDict["speed_up_key"])
        self.SpeedUpLabel.pack()

        self.bindSpeedDown = tk.Button(top, text="Bind speed down key", command=lambda: self.bindAction("speed_down_key", self.SpeedDownLabel))
        self.bindSpeedDown.pack()
        self.SpeedDownLabel = tk.Label(top, text=self.callingInstance.keySymDict["speed_down_key"])
        self.SpeedDownLabel.pack()

        self.bindSkipBack = tk.Button(top, text="Bind skip back key", command=lambda: self.bindAction("skip_back_key", self.SkipBackLabel))
        self.bindSkipBack.pack()
        self.SkipBackLabel = tk.Label(top, text=self.callingInstance.keySymDict["skip_back_key"])
        self.SkipBackLabel.pack()

        self.bindSkipForward = tk.Button(top, text="Bind skip forward key", command=lambda: self.bindAction("skip_forward_key", self.SkipForwardLabel))
        self.bindSkipForward.pack()
        self.SkipForwardLabel = tk.Label(top, text=self.callingInstance.keySymDict["skip_forward_key"])
        self.SkipForwardLabel.pack()

        self.bindPlay = tk.Button(top, text="Bind Play/Pause", command=lambda: self.bindAction("play_key", self.PlayLabel))
        self.bindPlay.pack()
        self.PlayLabel = tk.Label(top, text=self.callingInstance.keySymDict["play_key"])
        self.PlayLabel.pack()


        self.saveKeyBindsButton = tk.Button(top, text='Save Keybinds', command=self.saveKeyBinds)
        self.saveKeyBindsButton.pack()

        self.defaultKeyBindsButton = tk.Button(top, text='Restore Defaults', command=self.defaultKeyBinds)
        self.defaultKeyBindsButton.pack()

        self.closeKeyBindsButton = tk.Button(top, text='Close', command=self.closeKeyBinds)
        self.closeKeyBindsButton.pack()

    def bindAction(self, action, label):
        self.actionToBind = action
        self.labelToUpdate = label
        print(self.actionToBind)

    def bindKey(self, event):
        # self.callingInstance.play_key = event.keycode
        self.callingInstance.keysDict[self.actionToBind] = event.keycode
        self.callingInstance.keySymDict[self.actionToBind] = event.keysym
        self.labelToUpdate.config(text=event.keysym)
        # print(event.keysym)

    def saveKeyBinds(self):
        # print(os.path.join(os.getcwd(),'keyBinds.json'))
        keyBindsFile = os.path.join(os.getcwd(), 'keyBinds.json')
        with open(keyBindsFile, 'w') as fd:
            fd.write(json.dumps([self.callingInstance.keySymDict, self.callingInstance.keysDict]))
        self.top.destroy()

    def defaultKeyBinds(self):
        self.callingInstance.keySymDict = self.callingInstance.keySymDict_default
        self.callingInstance.keysDict = self.callingInstance.keysDict_default
        self.Object1Label.config(text=self.callingInstance.keySymDict["object_1_key"])
        self.Object2Label.config(text=self.callingInstance.keySymDict["object_2_key"])
        self.Object3Label.config(text=self.callingInstance.keySymDict["object_3_key"])
        self.Object4Label.config(text=self.callingInstance.keySymDict["object_4_key"])
        self.SpeedUpLabel.config(text=self.callingInstance.keySymDict["speed_up_key"])
        self.SpeedDownLabel.config(text=self.callingInstance.keySymDict["speed_down_key"])
        self.SkipBackLabel.config(text=self.callingInstance.keySymDict["skip_back_key"])
        self.SkipForwardLabel.config(text=self.callingInstance.keySymDict["skip_forward_key"])
        self.PlayLabel.config(text=self.callingInstance.keySymDict["play_key"])


    def closeKeyBinds(self):
        self.top.destroy()






app = chronotate()


