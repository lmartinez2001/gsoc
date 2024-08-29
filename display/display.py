import logging

import cv2
import numpy as np
import matplotlib.pyplot as plt

import mediapipe as mp
from mediapipe.python.solutions.drawing_utils import DrawingSpec

from threading import Thread, Event, Lock
import time


logger = logging.getLogger(__name__)

class Display(Thread):

    def __init__(self, width=800, height=600, display_name='Display'):
        super().__init__()
        self.display_name = display_name
        self._frame = np.zeros((width, height, 3))
        self.components = []
        self.stop_event = Event()
        self.lock = Lock()
        self.width = width
        self.height = height
        self.frame_count = 0
        self.fps = 0
        self.last_fps_update = time.time()
        logger.info('Display class initialized')


    @property
    def frame(self):
        with self.lock:
            return self._frame.copy()


    @frame.setter
    def frame(self, new_frame):
        with self.lock:
            self._frame = cv2.resize(new_frame, (self.width, self.height))
            self.frame_count += 1
            current_time = time.time()
            time_diff = current_time - self.last_fps_update
            if time_diff >= 1.0:  # update fps every second
                self.fps = self.frame_count / time_diff
                self.frame_count = 0
                self.last_fps_update = current_time



    def add_component(self, component):
        with self.lock:
            self.components.append(component)


    def run(self):
        while not self.stop_event.is_set():
            display_frame = self.frame.copy()
            for comp in self.components:
                comp(display_frame)

            cv2.imshow(self.display_name, display_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.stop_event.set()
                break
        cv2.destroyAllWindows()

       
    def stop(self):
        logger.info('Stopping display stream')
        self.stop_event.set()
