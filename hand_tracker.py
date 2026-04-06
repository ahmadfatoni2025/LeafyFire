import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import config
import os
import urllib.request

class HandTracker:
    def __init__(self):
        """Inisialisasi The Brain (Hand Landmarker MediaPipe)"""
        # Auto-download model jika tidak ditemukan
        if not os.path.exists(config.MODEL_PATH):
            print(f"Model {config.MODEL_PATH} tidak ditemukan. Mengunduh secara otomatis...")
            url = 'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task'
            urllib.request.urlretrieve(url, config.MODEL_PATH)
            print("Download selesai!\n")
            
        base_options = python.BaseOptions(model_asset_path=config.MODEL_PATH)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=config.MAX_HANDS,
            min_hand_detection_confidence=config.DETECTION_CONFIDENCE,
            min_hand_presence_confidence=config.TRACKING_CONFIDENCE,
            min_tracking_confidence=config.TRACKING_CONFIDENCE
        )
        self.detector = vision.HandLandmarker.create_from_options(options)

    def process(self, rgb_image):
        """Memproses gambar RGB untuk menemukan koordinat tangan"""
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
        return self.detector.detect(mp_image)

    def close(self):
        """Membersihkan memori setelah selesai"""
        self.detector.close()
