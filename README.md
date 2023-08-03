## Download the EXE:
[Click Here To Download The EXE](https://github.com/ShumanLab/Chronotate/raw/main/Chronotate.exe?download=)

<img src="https://user-images.githubusercontent.com/108362860/216124746-450dccf6-c007-4eee-b271-0ba784071acd.png" width="300">

**Chronotate** (chrono + notate) is a simple utility for generating timestamped annotations during video playback. This python application captures key down/up events to mark the start and stop time of events during video playback.  

This utility was developed to aid in the scoring of novel object recognition/ novel object location (NOR/NOL) tasks.  This program supports scoring interaction with up to four objects simultaneously, each bound to the ‘j’, ’k’, ‘l’, or ‘;’ key.  Holding the relevant key down generates a timestamp marking the beginning of an interaction bout, and releasing the key marks the end of the bout. These timestamps can then be exported to quantify bout durations, total interaction time, and minute-by-minute interaction as desired.

## Interface:
**Load video button:** This button launches an open file dialog to select a video for scoring. Supported file types include but are not limited to *.avi, *.mp4, and *.mkv  

**Play/Pause button:** This button starts and stops video playback.  

**Playback speed dropdown:** This menu allows the user to speed up or slow down the speed of video playback.   

**Progress Bar:** This bar tracks the current second of video playback and allows the user to scrub to a particular second of the video by dragging the slider.  

**Skip buttons:** These buttons allow the user to skip forwards or backwards in 5 second increments 

**Marker Pane:** This box displays the timecodes of recorded keyboard events.  Additionally, selecting an event from this box seeks the video playback to the recorded timecode, allowing the user to review the recorded event.  

**Export Button:** This button writes the recorded markers to a .csv file  

**Load Marker File:** This button loads the recorded events from a previously exported marker .csv file into the marker pane, allowing for the review of a previously scored video.  

![Chronotate_Interface](https://user-images.githubusercontent.com/108362860/216124015-6c562092-176f-4266-82f4-fb346da14304.png)


## System Compatibility:  

**Video Compatibility:**  
The file formats tested so far include avi, mkv, and mp4, but many more are likely compatible. We recommend against converting between file types, if possible, as information can be lost in transcoding. Behavior may be unpredictable if used with temporally compressed videos. 

**Operating System Compatibility:**  
The compiled .exe is compatible with Windows.  
The python scripts are compatible with OSX, Linux and Windows.
(See source version installation instructions for additional setup required on Mac and Linux)

## Installation:  
**Precompiled Version:**  
This software is distributed as a precompiled, standalone, executable file.  All that is required to begin using this software is to download the .exe.  Due to GitHub’s handling of large files, cloning or downloading the .zip of the repository will result in a broken exe. Therefore, the exe must be downloaded separately, which can be done by [clicking here](https://github.com/ShumanLab/Chronotate/raw/main/Chronotate.exe?download=)

**Source Version:**
In the case that greater flexibility is desired than the precompiled version offers, the source files are provided in this repositiory. In order to run these scripts it is recommended to set up a new Conda environment for Chronotate. The required dependencies are:  
* pandas  
* tkinter
* pyAV
* Pillow  
* the modified version of tkVideoPlayer hosted in this repository
**Additional steps on Mac and Linux:**
* Disable key repeat in your operating system's keyboard settings
* Remap keyboard bindings via the 'cusomize key bindings' interface
  
    
      
      
Please cite chronotate if you use it in your research


