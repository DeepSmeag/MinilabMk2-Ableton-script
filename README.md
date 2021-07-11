# MinilabMk2-Ableton-script
### This project is intended for those who are into music production, have a Minilab Mk2 MIDI controller and use Ableton Live as their DAW.
### This script comes as a modified version of the Ableton mode that the Minilab Mk2 controller offers to users, based on personal preferences and public suggestions.

# Features

## Pads:
- Only pads 1-8 control clips now, specifically the clips of the selected scene , pads 9-16 now have modified functionality
- Pads 1-8 now have different colors to signal the state of the clip: </br> 🔴🟠🟡🟢🔵🟣🟤⚫⚪🔘🛑⭕

🟥🟧🟨🟩🟦🟪🟫⬛⬜🔲🔳⏹☑✅❎

❤️🧡💛💚💜💙🤎🖤🤍♥️💔💖💘💝💗💓💟💕❣️♡

🔺🔻🔷🔶🔹🔸♦💠💎💧🧊
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
### 1. Download the folder and the minilab preset. 
### 2. Place the folder in your Ableton folder under \Resources\MIDI Remote Scripts\ 
### 3. Import the minilab preset using the MIDI Control Center and use it as the 8th bank
### 4. You are now ready to start Ableton and go to settings, control surfaces and select the script (you are looking for the folder's name)
- This means that you may change the folder's name as you desire, I only chose to name it so as to have it as the first script in the dropdown list (they are alphabetically ordered).
