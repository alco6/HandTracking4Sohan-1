import PIL
from PIL import Image,ImageTk
import cv2
from tkinter import *
import numpy as np
import threading
from pynput.mouse import Controller
from time import sleep

class CameraInterface:
    def __init__(self):
        self.lowerBound = np.array([29, 86, 6])
        self.upperBound = np.array([64, 255, 255])

        self.cam = cv2.VideoCapture(0)

        self.root = Tk()
        self.root.bind('<Escape>', lambda e: self.root.quit())
        self.root.bind("a", lambda x: self.pauseLoop())

        self.kernelOpen = np.ones((5, 5))
        self.kernelClose = np.ones((20, 20))

        self.font = cv2.FONT_HERSHEY_SIMPLEX

        self.lmain = Label(self.root)

        self.red = Button(self.root, text="red", command=self.detectRed)
        self.green = Button(self.root, text="green", command=self.detectGreen)
        self.blue = Button(self.root, text="blue", command=self.detectBlue)
        self.rgbContainer = Label(self.root, text="test")
        self.pauseButton = Button(self.root, text="pause", command=self.pauseLoop)

        # self.startCam = Button(self.root, text="start camera", command=self.startThread)

        self.lmain.grid(row=0, column=0, columnspan=2)
        self.red.grid(row=1, column=0, sticky='nesw')
        self.green.grid(row=2, column=0, sticky='nesw')
        self.blue.grid(row=3, column=0, sticky='nesw')
        self.rgbContainer.grid(row=1, column=1, rowspan=3, sticky='nesw')
        self.pauseButton.grid(row=4, column=0, columnspan=3, rowspan=2, sticky='nesw')

        # self.startCam.grid(row=4, column=0, columnspan=3)

        self.mouse = Controller()

        self.screenx = self.root.winfo_screenwidth()
        self.screeny = self.root.winfo_screenheight()

        self.camx = 340
        self.camy = 220

        self.pauseMode = False

    def detectRed(self):
        self.lowerBound = np.array([170, 120, 150])
        self.upperBound = np.array([190, 255, 255])

    def detectGreen(self):
        self.lowerBound = np.array([29, 86, 6])
        self.upperBound = np.array([64, 255, 255])

    def detectBlue(self):
        self.lowerBound = np.array([110, 150, 100])
        self.upperBound = np.array([120, 200, 200])

    def startThread(self):
        threadCam = threading.Thread(target=self.show_frame)
        threadCam.start()

    def pauseLoop(self):

        if self.pauseMode is False:
            print('paused')
            self.pauseMode = True
        else:
            print('started again')
            self.pauseMode = False
            self.show_frame()


    def nothing(self):
        pass

    def create_trackbar(self):

        # set trackbar
        hh = 'hue high'
        hl = 'hue low'
        sh = 'saturation high'
        sl = 'saturation low'
        vh = 'value high'
        vl = 'value low'
        thv = 'th1'

        # set ranges
        cv2.createTrackbar(hh, "color_hsv", self.upperBound[0], 179, self.nothing)
        cv2.createTrackbar(hl, "color_hsv", self.lowerBound[0], 179, self.nothing)
        cv2.createTrackbar(sh, "color_hsv", self.upperBound[1], 255, self.nothing)
        cv2.createTrackbar(sl, "color_hsv", self.lowerBound[1], 255, self.nothing)
        cv2.createTrackbar(vh, "color_hsv", self.upperBound[2], 255, self.nothing)
        cv2.createTrackbar(vl, "color_hsv", self.lowerBound[2], 255, self.nothing)
        cv2.createTrackbar(thv, "color_hsv", 127, 255, self.nothing)

    def show_frame(self):

        ret, img = self.cam.read()

        # flipping for the selfie cam right now to keep sane

        img = cv2.flip(img, 1)
        img = cv2.resize(img, (self.camx, self.camy))

        if not self.pauseMode:
            # convert BGR to HSV
            frame = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            # create the Mask
            mask = cv2.inRange(imgHSV, self.lowerBound, self.upperBound)
            # morphology
            maskOpen = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernelOpen)
            maskClose = cv2.morphologyEx(maskOpen, cv2.MORPH_CLOSE, self.kernelClose)

            maskFinal = maskClose
            conts, h = cv2.findContours(maskFinal.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

            cv2.drawContours(img, conts, -1, (255, 0, 0), 3)

            if conts:
                x, y, w, h = cv2.boundingRect(conts[0])
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                x1, y1, w1, h1 = cv2.boundingRect(conts[0])
                x1 = int(x1 + w1 / 2)
                y1 = int(y1 + h1 / 2)
                cv2.circle(img, (x1, y1), 2, (0, 0, 255), 2)
                mouseLoc = (self.screenx - (x1 * self.screenx / self.camx), y1 * self.screeny / self.camy)
                self.mouse.position = mouseLoc


            imgPIL = PIL.Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=imgPIL)
            self.lmain.imgtk = imgtk
            self.lmain.configure(image=imgtk)
            self.lmain.after(10, self.show_frame)




if __name__ == "__main__":

    camInt = CameraInterface()
    camInt.show_frame()
    camInt.root.mainloop()
