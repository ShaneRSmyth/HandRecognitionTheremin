#############################################################################################################################
#libraries
#computer vision
import cv2 as cv
#GUI
import tkinter as tk
#placing video capture on GUI
from PIL import Image, ImageTk
#different tk styles
from tkinter import ttk
#main class
import synth as syn
#midi
import pygame.midi
#############################################################################################################################

#GUI
#makes main window
window = tk.Tk()
#window title
window.title("Midi Hands")
#window attributes
window.config(bg = 'gold')

#graphics window
imageFrame = tk.Frame(window, highlightbackground = 'dark orange', highlightthickness=30)
imageFrame.grid()

#start video using default camera
cap = cv.VideoCapture(0)

#instance of class from 'HandTrackingModule'
detector = syn.HandDetector(detectionCon = 0.75, maxHands=2) #using an instance of the handDetector object.  Changing detection confidence = 0.75

#IDs of fingertips from mediapipe
fingerTips = [4, 8, 12, 16, 20]

#scales
CHROMATIC = [60, 61, 62, 63, 64, 65, 67, 68, 69, 70, 71, 72]
OCTAVEC = [60, 62, 64, 65, 67, 69, 71, 72]
PENTATONIC = [60, 62, 64, 67, 69]
scales = ["Chromatic", "OctaveC", "Pentatonic"]

#midi ports
pygame.midi.init()

player = pygame.midi.Output(0)
player.set_instrument(117) #10 #118 synth drum, 116 drum, 117


# def synth_drums():
#     player.set_instrument(117)

# def piano():
#     player.set_instrument(0)

def colours():
    #dark mode
    if var1.get() == 1:
        window.config(bg = "black")
        imageFrame.config(highlightbackground = "dark blue")
    #0
    else:
    #bright mode
        window.config(bg = "gold")
        imageFrame.config(highlightbackground = "dark orange")

def change_instrument():
    #get the value from dropbox
    chosenInstr = int(dropBoxVar.get())
    #set the instrument to that value
    player.set_instrument(chosenInstr) #7, 117, 0, 100

def change_scale():
    try:
        chosenScale = dropBoxVar2.get()

        #if the dropbox String matches the String in the first position of scales list
        if chosenScale == scales[0]:
            #scale gets set to CHROMATIC
            scale = CHROMATIC
        elif chosenScale == scales[1]:
            #scale gets set to OCTAVEC
            scale = OCTAVEC
        elif chosenScale == scales[2]:
            scale = PENTATONIC
        return scale
    except NameError:
        pass

def slider_value(change):
    #get the value from the slider, print it as an integer
    result = print(int(slider1.get()))

    return result

def slider2_value(change):
    #get the value from the slider, print it as an integer
    result = print(int(slider2.get()))

    return result

#############################################################################################################################
#findHands and findPosition, ID conditions
def main():

    # #read image
    _, imgRead = cap.read()

    hands, imgRead = detector.findHands(imgRead)  # with draw
    # hands = detector.findHands(img, draw=False)  # without draw


    if hands:
        # Hand 1
        hand1 = hands[0]
        lmList1 = hand1["lmList"]  # List of 21 Landmark points
        bbox1 = hand1["bbox"]  # Bounding box info x,y,w,h
        centerPoint1 = hand1['center']  # center of the hand cx,cy
        handType1 = hand1["type"]  # Handtype Left or Right

        fingers1 = detector.fingersUp(hand1)
        fingers1Count = fingers1.count(1)

        # for i in range(1, 6):
        #     if len(hands) == 1 and fingers1Count == i:
        #         player.note_on(scale[i], 127)
        #         cv.waitKey(1000)
        #         player.note_off(scale[i], 127)
            

        if len(hands) == 2:
            # Hand 2
            hand2 = hands[1]
            lmList2 = hand2["lmList"]  # List of 21 Landmark points
            bbox2 = hand2["bbox"]  # Bounding box info x,y,w,h
            centerPoint2 = hand2['center']  # center of the hand cx,cy
            handType2 = hand2["type"]  # Hand Type "Left" or "Right"

            length, info, imgRead = detector.findDistance(lmList1[8][0:2], lmList2[8][0:2], imgRead)  # with draw
            length2, info2, imgRead = detector.findDistance(lmList1[12][0:2], lmList1[0][0:2], imgRead)
            print(f"Volume Length: {length2}")

            fingers2 = detector.fingersUp(hand2)
            fingers2Count = fingers2.count(1)

            fingersTotal = (fingers1Count + fingers2Count)
            #displays the number of fingers in total on the screen
            cv.putText(imgRead, str(fingersTotal), (45, 375), cv.FONT_HERSHEY_PLAIN, 10, (0, 0, 0), 25)
            print(f"Length: {length}")

            try:
                scale = change_scale()
                print(f"Scale: {scale} of type: {type(scale)}")
                #max range
                rangetodetect = 250
                #length of the chosen scale
                numInScale = len(scale)
                print(f"Number in scale: {numInScale} of type: {type(numInScale)}")
                
                #length between 1 and 250
                if length >= 1 and length <= rangetodetect:

                    rangeJunk = int(rangetodetect/numInScale)
                    junk = round((length)/rangeJunk)-1
                    print(f"Junk: {junk}")
                    noteToPlay = scale[junk]
                    print(f"Note played: {noteToPlay} of type: {type(noteToPlay)}")


                    # player.set_instrument(117) #10 #118 synth drum, 116 drum, 117
                                #frequency   #volume
                    player.note_on(noteToPlay, int(length2))

                    #added this to stop reverb
                    cv.waitKey(10)
                    player.note_off(noteToPlay, int(length2))
            except TypeError:
                pass
            
            try:
                slider1.set(length)

                slider2.set(length2)
            except NameError:
                pass

        else:
            cv.putText(imgRead, str(fingers1Count), (45, 375), cv.FONT_HERSHEY_PLAIN, 10, (0, 0, 0), 25)
            
    '''
    places video capture on GUI   
    '''
    cv2image = cv.cvtColor(imgRead, cv.COLOR_BGR2RGBA)
    img = Image.fromarray(cv2image)  
    imgtk = ImageTk.PhotoImage(image = img)

    labelMain = tk.Label(imageFrame)
    labelMain.grid(row = 0, column = 0)

    labelMain.imgtk = imgtk
    labelMain.configure(image = imgtk)
    #exits program
    labelMain.after(10, main)
#############################################################################################################################

#call main()
main()


canvas = tk.Canvas(window, width=450, height=450, bg = "black")
canvas.grid(row = 0, column = 1, sticky = tk.N + tk.S, columnspan = 1)


#creates a slider, 50-100 scale
#frequency slider
slider1 = ttk.Scale(canvas, length = 250, from_ = 1, to = 250, orient = 'vertical', variable = tk.DoubleVar, command = slider_value)
slider1.grid(row = 0, column = 10, padx = 50, pady = 10)

#volume slider (velocity of chosen instrument)
slider2 = ttk.Scale(canvas, length = 250, from_ = 100, to = 50, orient = 'vertical', variable = tk.DoubleVar, command = slider2_value)
slider2.grid(row = 0, column = 11, padx = 50, pady = 10)


#Midi hands label
midiVar = tk.StringVar()
midiVar.set("Midi Hands")

midiLabel = ttk.Label(imageFrame, textvariable = midiVar, foreground = "blue", background = "white", anchor="center")
midiLabel.config(font = ('Helvetica', 20))
midiLabel.grid(sticky = tk.E + tk.W)


#volume label
volumeVar = tk.StringVar()
volumeVar.set("Volume")

volumeLabel = ttk.Label(canvas, textvariable = volumeVar, foreground = "white", background = "black")
volumeLabel.config(font = ('Helvetica', 15))
volumeLabel.grid(row = 1, column = 11)


pitchVar = tk.StringVar()
pitchVar.set("Pitch")

pitchLabel = ttk.Label(canvas, textvariable = pitchVar, foreground = "white", background = "black")
pitchLabel.config(font = ('Helvetica', 15))
pitchLabel.grid(row = 1, column = 10)


# pianoButton = ttk.Button(canvas, text = "Piano", command = piano)
# pianoButton.grid(row = 0, column = 0)


# synthDrumsButton = ttk.Button(canvas, text = "Synth Drums", command = synth_drums)
# synthDrumsButton.grid(row = 1, column = 0)


#empty list
instrumentList = []

#put numbers up to 128 inside empty list
for instrument in range(128):
    instrumentList.append(instrument)

dropBoxVar = tk.StringVar()
dropBoxVar.set(instrumentList[0])

dropBox = tk.OptionMenu(window, dropBoxVar, *instrumentList)
dropBox.grid(column=0, row=1)

dropButton = tk.Button(window, text = "Set Instrument", command = change_instrument)
dropButton.grid(column=0, row=2)


dropBoxVar2 = tk.StringVar()
dropBoxVar2.set(scales[0])

dropBox2 = tk.OptionMenu(window, dropBoxVar2, *scales)
dropBox2.grid(column = 1, row = 1, columnspan = 1)

dropButton2 = tk.Button(window, text = "Set Scale", command = change_scale)
dropButton2.grid(column = 1, row = 2, columnspan = 1)


var1 = tk.IntVar()

darkMode = tk.Checkbutton(imageFrame, text = "Dark Colours", variable = var1, onvalue = 1, offvalue = 0, command = colours)
darkMode.grid(column = 0, row = 3)


#keeps GUI open
window.mainloop()