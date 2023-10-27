import cv2
import os
from pynput import keyboard


class key_checker():
    def __init__(self) -> None:
        # ...or, in a non-blocking fashion:
        self.listener = keyboard.Listener(
                    on_press=self.on_press,
                    on_release=self.on_release)
        self.listener.start()
        self.command = []

    def on_press(self, key):
        try:
            if key.char == 'a':
                self.command.append('capture')  
        except AttributeError:
            pass

    def on_release(self, key):
        pass
            
    def join(self):
        self.listener.join()

    def stop(self):
        self.listener.stop()

    def get_command(self):
        command = self.command
        self.command = [] # empty command queue
        print(command)
        return command[-1]

key_check = key_checker()
cap = cv2.VideoCapture(6)

onlyfiles = [int(f.replace('.jpg','')) for f in os.listdir('captured_images/data') if os.path.isfile(os.path.join('captured_images', f))]
if onlyfiles != []:
    count = max(onlyfiles)
else:
    count = 0
while cap.isOpened():
    ret, frame = cap.read()
    if ret:
        cv2.imshow('camera image', frame)
        cv2.waitKey(1)
        if len(key_check.command) > 0 and key_check.get_command() == "capture":
            count = count + 1
            cv2.imwrite(os.path.join('captured_images', str(count) + '.jpg'), frame)