import cv2, sys
import pygame
from threading import Thread
import time

class Video:
    def __init__(self, video_path, audio_path):
        self.video_path = video_path
        self.audio_path = audio_path
        self.video_end = False

    def play_audio(self, start_time=None):
        pygame.mixer.init()
        pygame.mixer.music.load(self.audio_path)
        if start_time:
            pygame.mixer.music.play(start=start_time)
        else:
            pygame.mixer.music.play()

    def play(self):
        cap = cv2.VideoCapture(self.video_path)

        if not cap.isOpened():
            print("Error: Could not open video.")
            sys.exit()

        screen_width = 1313
        screen_height = 750

        cv2.namedWindow('Video Player', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Video Player', screen_width, screen_height)
        cv2.setWindowProperty('Video Player', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_duration = 1 / fps

        audio_thread = Thread(target=self.play_audio())
        audio_thread.start()

        start_time = time.time()

        while True:
            ret, frame = cap.read()
            if not ret:
                print("End of video.")
                self.video_end = True
                break

            resized_frame = cv2.resize(frame, (screen_width, screen_height))
            cv2.imshow('Video Player', resized_frame)

            elapsed_time = time.time() - start_time
            expected_frame = int(elapsed_time * fps)

            time.sleep(max(0, frame_duration - (time.time() - (start_time + expected_frame * frame_duration))))

            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                self.video_end = True
                break

            if cv2.getWindowProperty('Video Player', cv2.WND_PROP_VISIBLE) < 1:
                print("Window closed.")
                break

        cap.release()
        cv2.destroyAllWindows()
        pygame.mixer.music.stop()