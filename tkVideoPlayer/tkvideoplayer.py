# this version of tkVideoPlayer is a modified version based off release 2.2

import av
import time
import threading
import logging
import tkinter as tk
from PIL import ImageTk, Image, ImageOps
from typing import Tuple, Dict

logging.getLogger('libav').setLevel(logging.ERROR)  # removes warning: deprecated pixel format used


class TkinterVideo(tk.Label):

    def __init__(self, master, scaled: bool = True, consistant_frame_rate: bool = True, keep_aspect: bool = False, *args, **kwargs):
        super(TkinterVideo, self).__init__(master, *args, **kwargs)

        self.playback_speed_2 = 1
        self.path = ""
        self._load_thread = None

        self._loaded = False
        self._paused = True
        self._stop = True

        self.consistant_frame_rate = consistant_frame_rate # tries to keep the frame rate consistant by skipping over a few frames

        self._container = None

        self._current_img = None
        self._current_frame_Tk = None
        self._frame_number = 0
        self._time_stamp = 0

        self._current_frame_size = (0, 0)

        self._seek = False
        self._seek_sec = 0

        self._video_info = {
            "duration": 0, # duration of the video
            "framerate": 0, # frame rate of the video
            "framesize": (0, 0) # tuple containing frame height and width of the video

        }   

        self.set_scaled(scaled)
        self._keep_aspect_ratio = keep_aspect
        self._resampling_method: int = Image.NEAREST


        self.bind("<<Destroy>>", self.stop)
        self.bind("<<FrameGenerated>>", self._display_frame)
    
    def keep_aspect(self, keep_aspect: bool):
        """ keeps the aspect ratio when resizing the image """
        self._keep_aspect_ratio = keep_aspect

    def set_resampling_method(self, method: int):
        """ sets the resampling method when resizing """
        self._resampling_method = method

    def set_size(self, size: Tuple[int, int], keep_aspect: bool=False):
        """ sets the size of the video """
        self.set_scaled(False, self._keep_aspect_ratio)
        self._current_frame_size = size
        self._keep_aspect_ratio = keep_aspect

    def _resize_event(self, event):

        self._current_frame_size = event.width, event.height

        if self._paused and self._current_img and self.scaled:
            if self._keep_aspect_ratio:
                proxy_img = ImageOps.contain(self._current_img.copy(), self._current_frame_size)

            else:
                proxy_img = self._current_img.copy().resize(self._current_frame_size)
            
            self._current_imgtk = ImageTk.PhotoImage(proxy_img)
            self.config(image=self._current_imgtk)


    def set_scaled(self, scaled: bool, keep_aspect: bool = False):
        self.scaled = scaled
        self._keep_aspect_ratio = keep_aspect
        
        if scaled:
            self.bind("<Configure>", self._resize_event)

        else:
            self.unbind("<Configure>")
            self._current_frame_size = self.video_info()["framesize"]


    def _set_frame_size(self, event=None):
        """ sets frame size to avoid unexpected resizing """

        self._video_info["framesize"] = (self._container.streams.video[0].width, self._container.streams.video[0].height)

        self.current_imgtk = ImageTk.PhotoImage(Image.new("RGBA", self._video_info["framesize"], (255, 0, 0, 0)))
        self.config(width=150, height=100, image=self.current_imgtk)

    def _load(self, path):
        """ load's file from a thread """
        # print('starting thread')
        current_thread = threading.current_thread()

        with av.open(path) as self._container:

            self._container.streams.video[0].thread_type = "AUTO"
            
            # print(self._container.duration)
            # print(self._container.start_time)
            self._container.fast_seek = False
            #self._container.fast_seek = False
            self._container.discard_corrupt = True

            self.stream = self._container.streams.video[0]


            try:
                self._video_info["framerate"] = float(self.stream.average_rate)

            except TypeError:
                raise TypeError("Not a video file")
            
            try:

                #self._video_info["duration"] = float(self.stream.duration * self.stream.time_base)
                self._video_info["duration"] = float(self._container.duration/1000000) #container.duration seems to work for all filetypes inc mkv
                self.event_generate("<<Duration>>")  # duration has been found
                # print('duration found')

            except (TypeError, tk.TclError):  # the video duration cannot be found, this can happen for mkv files
                # print('duration NOT found')
                pass


            self._frame_number = 0

            self._set_frame_size()

            self.stream_base = self.stream.time_base

            try:
                self.event_generate("<<Loaded>>") # generated when the video file is opened
            
            except tk.TclError:
                pass

            now = time.time_ns() // 1_000_000  # time in milliseconds
            then = now

            # print(self._load_thread == current_thread)
            # print(self._load_thread)
            # print(current_thread)
            while self._load_thread == current_thread and not self._stop:
                if self._seek: # seek to specific second
                    #print(float(frame.pts * self.stream.time_base))
                    #print(frame.pts)
                    #print(self.stream.time_base)
                    # print(self._seek_sec * 1000000)
                    # print(self._seek_sec)
                    #self._container.seek(self._seek_sec*1000000 , whence='time', backward=True, any_frame=False) # the seek time is given in av.time_base, the multiplication is to correct the frame

                    #self._container.seek(int(self._seek_sec * 1000000), whence='time', backward=False, any_frame=False)  # the seek time is given in av.time_base, the multiplication is to correct the frame
                    self._container.seek(int(self._seek_sec * 1000000), whence='time', backward=True, any_frame=False)  # the seek time is given in av.time_base, the multiplication is to correct the frame
                    for j, frame in enumerate(self.iter_frames()): #seek brings us to previous keyframe, follow by demuxing/decoding to desired position
                        if j > 300:
                            # print('Did not find target within 300 frames of seek.')
                            # print(float(frame.pts * self.stream.time_base))
                            break
                        if frame.pts * self.stream.time_base >= self._seek_sec:
                            #print('Found target in', j, 'frames.')
                            #print(float(frame.pts * self.stream.time_base))
                            break

                    #print(self._time_stamp)
                    self._seek = False
                    self._frame_number = int(round(self._video_info["framerate"] * self._seek_sec))

                    self._seek_sec = 0

                # print(self._paused)
                if self._paused:
                    time.sleep(0.0001)  # to allow other threads to function better when its paused
                    continue

                now = time.time_ns() // 1_000_000  # time in milliseconds
                delta = now - then  # time difference between current frame and previous frame
                then = now

                # print(delta)
                if self.play_start:
                    #then = now
                    delta = 0
                    self.play_start = False

                #print(1 / (self.playback_speed_2*self._video_info["framerate"]))
                #print(delta / 1000)
                #print(self.playback_speed_2)
                #print(self._video_info["framerate"])

                #print( (delta / 1000) - (1 / (self.playback_speed_2 * self._video_info["framerate"]) ) )


                #if self.consistant_frame_rate and (delta / 1000 >= 1 / self._video_info["framerate"]):





                try:

                    if self.consistant_frame_rate and (delta / 1000 >= 1 / (self.playback_speed_2 * self._video_info[
                        "framerate"])):  # skip frames for faster playback speeds
                        #     # skips frames if to keep a consistant frame rate
                        # frames_to_skip = int( ( (1 / (self.playback_speed_2 * self._video_info["framerate"]) ) / (delta / 1000) ) )
                        frames_to_skip = int(
                            (delta / 1000) / (1 / (self.playback_speed_2 * self._video_info["framerate"])))
                        #print(frames_to_skip)
                        k = 0
                        for x in range(frames_to_skip):
                            frame = next(self._container.decode(video=0))
                            self._frame_number += 1
                            k += 1
                        #print('skipped', k, 'frames')
                        # print('skip')

                    else:
                        frame = next(self._container.decode(video=0))

                        self._current_img = frame.to_image()

                        self.event_generate("<<FrameGenerated>>")
                        # print('frame generated')
                        self._frame_number += 1



                    self._time_stamp = float(frame.pts * self.stream.time_base)


                    #print('not skipped')


                    #print(self.playback_speed_2)


                    time.sleep(max( (1/ (self._video_info["framerate"] * self.playback_speed_2)) - (delta / 1000),0)  ) #this one
                    #time.sleep(max((((1/self._video_info["framerate"])*1000) - delta) / 1000, 0)) #v2.3 equivalent

                    #time.sleep(.000000000001)
                    #print(self.playback_speed_2* (((1 / self._video_info["framerate"])) - (delta / 1000)) )


                    self.event_generate("<<Update>>")

                    if self._frame_number % self._video_info["framerate"] == 0:
                        self.event_generate("<<SecondChanged>>")

                except (StopIteration, av.error.EOFError, tk.TclError):
                    break

        self._frame_number = 0
        self._paused = True
        self._load_thread = None

        self._container = None

        try:
            self.event_generate("<<Ended>>")  # this is generated when the video ends

        except tk.TclError:
            pass

    def load(self, path: str):
        """ loads the file from the given path """
        self.stop()
        self.path = path
        # print(self._video_info["framerate"])
        self._load_thread = None
        self._loaded = False
        # time.sleep(0.0001)
        time.sleep(0.1)  # need to let previous thread finish
        self.play()

    def stop(self):
        """ stops reading the file """
        self._paused = True
        self._stop = True

    def pause(self):
        """ pauses the video file """
        self._paused = True

    def play(self):
        """ plays the video file """
        # print('playing')
        self._seek = False
        self._paused = False
        self._stop = False
        self.play_start = True

        if not self._load_thread:
            # print("loading new thread...")
            self._load_thread = threading.Thread(target=self._load,  args=(self.path, ), daemon=True)
            self._load_thread.start()
            # threading.Event().wait(0.01)
            # print(self._load_thread)

    def is_paused(self):
        """ returns if the video is paused """
        return self._paused

    def video_info(self) -> Dict:
        """ returns dict containing duration, frame_rate, file"""
        return self._video_info

    def metadata(self) -> Dict:
        """ returns metadata if available """
        if self._container:
            return self._container.metadata

        return {}

    def current_frame_number(self) -> int:
        """ return current frame number """
        return self._frame_number

    def current_duration(self) -> float:
        """ returns current playing duration in sec """
        return self._time_stamp
    
    def current_img(self) -> Image:
        """ returns current frame image """
        return self._current_img
    
    def _display_frame(self, event):
        """ displays the frame on the label """

        if self.scaled or (len(self._current_frame_size) == 2 and all(self._current_frame_size)):

            if self._keep_aspect_ratio:
                self._current_img = ImageOps.contain(self._current_img, self._current_frame_size, self._resampling_method)

            else:
                self._current_img =  self._current_img.resize(self._current_frame_size, self._resampling_method)

        else: 
            self._current_frame_size = self.video_info()["framesize"] if all(self.video_info()["framesize"]) else (1, 1)
            
            if self._keep_aspect_ratio:
                self._current_img = ImageOps.contain(self._current_img, self._current_frame_size, self._resampling_method)

            else:
                self._current_img =  self._current_img.resize(self._current_frame_size, self._resampling_method)


        self.current_imgtk = ImageTk.PhotoImage(self._current_img)
        self.config(image=self.current_imgtk)
        if not self._loaded:
            self.pause()
            self._loaded = True


    def seek(self, sec: int):
        """ seeks to specific time""" 

        self._seek = True
        # self._seek_sec = sec
        self._seek_sec = max(sec,0)
        
    def set_speed(self, speed):
        self.playback_speed_2 = speed

    def iter_frames(self): #iterate through frames to seek to precise time
        for packet in self._container.demux(self.stream):
            for frame in packet.decode():
                yield frame
            