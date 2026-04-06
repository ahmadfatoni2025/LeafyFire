CAMERA_INDEX = 0

# Pengaturan Performa Model AI
MAX_HANDS = 2
DETECTION_CONFIDENCE = 0.5
TRACKING_CONFIDENCE = 0.5

# Resolusi Kamera - Diturunkan sedikit agar jauh lebih ringan (640x480)
# Ini adalah resolusi standar optimal untuk MediaPipe & Pemrosesan Gambar
FRAME_WIDTH = 4000 
FRAME_HEIGHT = 6000

# Path dari model mediapipe tasks
MODEL_PATH = 'hand_landmarker.task'

# Fire Effect Config
FIRE_SCALE = 0.4  # Render resolusi api menjadi 40% dari resolusi asli (sangat meringankan CPU)
