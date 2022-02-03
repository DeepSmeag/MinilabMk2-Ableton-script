#####Last update: February 3rd, 2022

# MinilabMk2-Ableton-script
### This project is intended for those who are into music production, have a Minilab Mk2 MIDI controller and use Ableton Live as their DAW.
### This script comes as a modified version of the Ableton mode that the Minilab Mk2 controller offers to users, based on personal preferences and public suggestions.

# Features

## Pads:
- Only pads 1-8 control clips now, specifically the clips of the selected scene , pads 9-16 now have modified functionality
- Pads 1-8 now have different colors to signal the state of the clip: </br> 

  #### 🟢Playing - green🟢;</br> 
  #### 🔴Recording - red;🔴</br>
  #### 🟣Will record when triggered - magenta/purple;🟣</br>
  #### 🔵Triggered but not yet playing - cyan;🔵</br> 
- When a pad is pressed while the clip is playing it will now trigger the **stop** instead of trigger playing again
- Pads 9-16 control, in this order:
 ##### Global play (9) -> global stop (10) -> global record (11) -> global overdub (12) -> toggle between arrangement and session view (13) -> mute selected track (14) -> solo selected track (15) -> arm selected track (16).
- All pads 9-16 are permanently colored to give info about the current state of the thing they control

#### Pad 9 = global play : 🟩green - playing🟩, 🟨yellow - paused🟨
#### Pad 10 = global stop : 🟥red- playing (as in push to stop)🟥, 🟨yellow - not playing but cursor is not at the start (push to go back to beginning)🟨, ⬜white - not playing and cursor at start⬜
#### Pad 11 = global record: 🟦cyan - not recording🟦, 🟥red - recording🟥
#### Pad 12 = global overdub: 🟦blue - off🟦, 🟨yellow - on🟨
#### Pad 13 = view : 🟦cyan - arrangement🟦, 🟪magenta/purple - session🟪
#### Pad 14 = mute selected track: 🟩green - not muted🟩, 🟥red - muted🟥, 🟦cyan - muted by other track's solo only🟦, 🟦blue - muted by button and other track's solo🟦
#### Pad 15 = solo selected track: ⬜white - not soloed⬜, 🟦blue - soloed🟦
#### Pad 16 = arm selected track: 🟩green - not armed🟩, 🟥red - armed🟥

## Encoders:
#### Encoders 1,9 buttons (pushed): when in arrangement view, select track up/down ; when in session view, select scene up/down
- All encoders except for 16 keep their normal functions
#### Encoder 16 = control master volume
# **All LEDs will update accordingly to their function's state; they will update even if you use another controller or mouse/keyboard to change something**

### Colors can be modified in the script files

# Setup
### 0. Go to Versions and select the script version you need (based on Live version)
### 1. Download the corresponding folder and the minilab preset. (or the whole repository)
### 2. Place the folder in your Ableton folder under \Resources\MIDI Remote Scripts\ 
### 3. Import the minilab preset using the MIDI Control Center and use it as the 8th bank
### 4. You are now ready to start Ableton and go to preferences, MIDI, control surface and select the script (you are looking for the folder's name). Input and Output has to be from MiniLab Mk2
- This means that you may change the folder's name as you desire, I only chose to name it this way so as to have it as the first script in the dropdown list (they are alphabetically ordered).

# Disclaimer
- I am an enthusiast, hobbyist, member of the community. I am not a professional programmer for Arturia or Ableton and I do not own software created by them.
- I do use some code written by Arturia and Ableton's API, but most of the project is my own work.
- I do not profit from this project in any financial way.
- Anyone may use and modify my code to develop their own scripts based on their own preferences, as long as credit is provided if the work is published.
- The use of Arturia's and Ableton's property comes at the companies' own discretion.


# For Developers
### Here are some useful resources for learning about these kinds of scripts
- https://julienbayle.studio/PythonLiveAPI_documentation/Live10.1.19.xml
- http://remotescripts.blogspot.com/
- https://livecontrol.q3f.org/ableton-liveapi/articles/introduction-to-the-framework-classes/
- https://forum.arturia.com/index.php?topic=93714.0
- https://forum.ableton.com/viewtopic.php?t=200513
#### The code is written in Python


### [Link to original forum post](https://forum.arturia.com/index.php?topic=102839.0)

### For suggestions, issues and others, please use the Issues section. It helps with organization.

# Links to related projects by other members of the community:

@soneu03: https://github.com/soneu03/Ableton_Minilab_project
