"""
🔥 THE FIREBENDER AI 🔥
========================
Fantasy-style fire particle effects on hand movements
using MediaPipe hand tracking and OpenCV.

Controls:
  - Move your hand to cast fire
  - Open palm = intense fire burst
  - Fist = smoldering embers
  - Q = Quit
  - F = Toggle fullscreen
  - D = Toggle debug info
  - 1/2/3 = Fire style (Classic / Blue / Green)
"""

import cv2
import mediapipe as mp
import random
import numpy as np
import math
import time

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

CAMERA_INDEX = 0
MAX_HANDS = 2
DETECTION_CONFIDENCE = 0.7
TRACKING_CONFIDENCE = 0.6

# Particle settings
MAX_PARTICLES = 600
PARTICLES_PER_FINGER = 4
EMBER_CHANCE = 0.3      # Chance of spawning ember sparks
SMOKE_CHANCE = 0.15      # Chance of spawning smoke particles

# Fire color palettes (BGR format)
FIRE_PALETTES = {
    "classic": {
        "core":    [(255, 255, 255), (200, 255, 255), (130, 255, 255)],  # White-Yellow core
        "mid":     [(0, 220, 255), (0, 180, 255), (0, 140, 255)],       # Orange mid
        "outer":   [(0, 80, 200), (0, 40, 180), (0, 0, 150)],           # Red outer
        "ember":   [(0, 100, 255), (0, 200, 255), (50, 255, 255)],      # Bright ember
        "smoke":   [(80, 80, 90), (60, 60, 70), (40, 40, 50)],          # Grey smoke
        "glow":    (0, 120, 255),                                         # Overall glow tint
    },
    "blue": {
        "core":    [(255, 255, 255), (255, 255, 200), (255, 230, 180)],
        "mid":     [(255, 180, 50), (255, 140, 0), (255, 100, 0)],
        "outer":   [(200, 60, 0), (150, 30, 0), (100, 10, 0)],
        "ember":   [(255, 200, 100), (255, 150, 50), (255, 255, 200)],
        "smoke":   [(90, 80, 70), (70, 60, 50), (50, 40, 30)],
        "glow":    (255, 100, 20),
    },
    "green": {
        "core":    [(255, 255, 255), (200, 255, 200), (150, 255, 150)],
        "mid":     [(0, 255, 100), (0, 220, 50), (0, 180, 30)],
        "outer":   [(0, 120, 0), (0, 80, 0), (0, 40, 0)],
        "ember":   [(100, 255, 100), (50, 255, 50), (200, 255, 200)],
        "smoke":   [(60, 80, 60), (40, 60, 40), (30, 50, 30)],
        "glow":    (0, 200, 50),
    },
}

# Fingertip landmark indices in MediaPipe
FINGERTIPS = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
FINGER_BASES = [2, 5, 9, 13, 17]  # Corresponding base joints


# ═══════════════════════════════════════════════════════════════
# PARTICLE CLASSES
# ═══════════════════════════════════════════════════════════════

class FireParticle:
    """Main fire particle with realistic physics and color transitions."""

    def __init__(self, x, y, velocity_scale=1.0, palette="classic"):
        self.x = x + random.uniform(-8, 8)
        self.y = y + random.uniform(-5, 5)

        # Velocity with turbulence
        angle = random.uniform(-math.pi * 0.8, -math.pi * 0.2)  # Mostly upward
        speed = random.uniform(3, 10) * velocity_scale
        self.vx = math.cos(angle) * speed + random.uniform(-2, 2)
        self.vy = math.sin(angle) * speed

        # Size decreases over life
        self.radius = random.uniform(4, 14) * velocity_scale
        self.max_radius = self.radius

        # Life system
        self.life = 1.0
        self.decay = random.uniform(0.03, 0.07)

        # Visual properties
        self.palette_name = palette
        self.alpha = 1.0

        # Turbulence
        self.turbulence_phase = random.uniform(0, math.pi * 2)
        self.turbulence_speed = random.uniform(2, 5)

    def update(self):
        # Apply turbulence (flickering motion)
        self.turbulence_phase += self.turbulence_speed * 0.1
        turbulence_x = math.sin(self.turbulence_phase) * 1.5
        
        # Gravity pulls fire upward (negative y), with slight deceleration
        self.vy *= 0.97
        self.vx *= 0.95
        
        self.x += self.vx + turbulence_x
        self.y += self.vy
        
        # Reduce life
        self.life -= self.decay
        
        # Radius shrinks
        life_ratio = max(0, self.life)
        self.radius = self.max_radius * life_ratio
        self.alpha = life_ratio

    def draw(self, overlay, palette):
        if self.life <= 0 or self.radius < 0.5:
            return

        x, y = int(self.x), int(self.y)
        r = max(1, int(self.radius))

        # Color based on life phase
        if self.life > 0.75:
            color = random.choice(palette["core"])
        elif self.life > 0.4:
            color = random.choice(palette["mid"])
        else:
            color = random.choice(palette["outer"])

        # Draw with slight transparency via overlay
        cv2.circle(overlay, (x, y), r, color, -1, cv2.LINE_AA)

        # Inner brighter core for new particles
        if self.life > 0.7 and r > 3:
            core_color = palette["core"][0]
            cv2.circle(overlay, (x, y), max(1, r // 2), core_color, -1, cv2.LINE_AA)

    @property
    def is_dead(self):
        return self.life <= 0


class EmberParticle:
    """Small bright sparks that fly off quickly."""

    def __init__(self, x, y, palette="classic"):
        self.x = x
        self.y = y
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(5, 15)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - random.uniform(2, 6)
        self.life = 1.0
        self.decay = random.uniform(0.05, 0.12)
        self.radius = random.uniform(1, 3)
        self.palette_name = palette

    def update(self):
        self.vy += 0.15  # Gravity pulls embers down slightly
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.96
        self.vy *= 0.96
        self.life -= self.decay

    def draw(self, overlay, palette):
        if self.life <= 0:
            return
        x, y = int(self.x), int(self.y)
        r = max(1, int(self.radius * self.life))
        color = random.choice(palette["ember"])
        cv2.circle(overlay, (x, y), r, color, -1, cv2.LINE_AA)
        # Bright center
        cv2.circle(overlay, (x, y), max(1, r // 2), (255, 255, 255), -1, cv2.LINE_AA)

    @property
    def is_dead(self):
        return self.life <= 0


class SmokeParticle:
    """Slow-moving smoke wisps above the fire."""

    def __init__(self, x, y, palette="classic"):
        self.x = x + random.uniform(-15, 15)
        self.y = y - random.uniform(10, 30)
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-4, -1)
        self.life = 1.0
        self.decay = random.uniform(0.01, 0.03)
        self.radius = random.uniform(15, 35)
        self.palette_name = palette

    def update(self):
        self.x += self.vx + random.uniform(-0.5, 0.5)
        self.y += self.vy
        self.vx *= 0.99
        self.life -= self.decay
        self.radius += 0.5  # Smoke expands

    def draw(self, overlay, palette):
        if self.life <= 0:
            return
        x, y = int(self.x), int(self.y)
        r = max(1, int(self.radius))
        alpha = max(0, min(255, int(self.life * 80)))
        color = random.choice(palette["smoke"])
        # Draw semi-transparent smoke
        smoke_overlay = overlay.copy()
        cv2.circle(smoke_overlay, (x, y), r, color, -1, cv2.LINE_AA)
        cv2.addWeighted(smoke_overlay, self.life * 0.3, overlay, 1 - self.life * 0.3, 0, overlay)

    @property
    def is_dead(self):
        return self.life <= 0


# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def calculate_hand_velocity(current_pos, prev_pos, dt=1.0):
    """Calculate velocity between two hand positions."""
    if prev_pos is None:
        return 0.0
    dx = current_pos[0] - prev_pos[0]
    dy = current_pos[1] - prev_pos[1]
    return math.sqrt(dx * dx + dy * dy) / max(dt, 0.001)


def count_open_fingers(hand_landmarks, frame_shape):
    """Count how many fingers are extended (open)."""
    ih, iw = frame_shape[:2]
    open_count = 0
    
    for tip_idx, base_idx in zip(FINGERTIPS, FINGER_BASES):
        tip = hand_landmarks[tip_idx]
        base = hand_landmarks[base_idx]
        
        if tip_idx == 4:  # Thumb: check x distance
            if abs(tip.x - base.x) > 0.05:
                open_count += 1
        else:  # Other fingers: check if tip is above base
            if tip.y < base.y:
                open_count += 1
    
    return open_count


def apply_glow_effect(frame, fire_layer, glow_color, intensity=1.0):
    """Apply a cinematic glow effect using additive blending."""
    # Blur the fire layer for glow
    glow = cv2.GaussianBlur(fire_layer, (0, 0), sigmaX=25, sigmaY=25)
    glow2 = cv2.GaussianBlur(fire_layer, (0, 0), sigmaX=45, sigmaY=45)
    
    # Additive blending - this creates the magical glow
    result = cv2.add(frame, fire_layer)
    result = cv2.add(result, (glow * 0.5).astype(np.uint8))
    result = cv2.add(result, (glow2 * 0.3).astype(np.uint8))
    
    return result


def draw_magic_circle(frame, cx, cy, radius, color, alpha=0.3):
    """Draw a subtle magic circle around the active hand."""
    overlay = frame.copy()
    cv2.circle(overlay, (cx, cy), radius, color, 2, cv2.LINE_AA)
    # Draw inner ring
    cv2.circle(overlay, (cx, cy), int(radius * 0.6), color, 1, cv2.LINE_AA)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)


def draw_hud(frame, fps, particle_count, fire_style, debug_mode):
    """Draw on-screen HUD information."""
    h, w = frame.shape[:2]
    
    # Semi-transparent background bar at top
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 40), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
    
    # Title
    cv2.putText(frame, "THE FIREBENDER AI", (10, 28),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 180, 255), 2, cv2.LINE_AA)
    
    # Fire style indicator
    style_colors = {"classic": (0, 140, 255), "blue": (255, 140, 0), "green": (0, 200, 50)}
    style_color = style_colors.get(fire_style, (255, 255, 255))
    cv2.putText(frame, f"[{fire_style.upper()}]", (w - 150, 28),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, style_color, 1, cv2.LINE_AA)
    
    if debug_mode:
        # Debug info
        cv2.putText(frame, f"FPS: {fps:.0f}", (10, 65),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
        cv2.putText(frame, f"Particles: {particle_count}", (10, 85),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
    
    # Controls hint at bottom
    cv2.putText(frame, "Q:Quit  F:Fullscreen  D:Debug  1/2/3:Style",
                (10, h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1, cv2.LINE_AA)


# ═══════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════

def main():
    print("🔥 THE FIREBENDER AI 🔥")
    print("========================")
    print("Starting webcam...")
    print("Controls: Q=Quit, F=Fullscreen, D=Debug, 1/2/3=Fire Style")
    print()

    # Initialize MediaPipe Tasks API
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
    
    base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=MAX_HANDS,
        min_hand_detection_confidence=DETECTION_CONFIDENCE,
        min_hand_presence_confidence=TRACKING_CONFIDENCE,
        min_tracking_confidence=TRACKING_CONFIDENCE
    )
    detector = vision.HandLandmarker.create_from_options(options)

    # Initialize camera
    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)

    if not cap.isOpened():
        print("❌ Error: Cannot open camera!")
        return

    # State
    particles = []
    prev_hand_positions = {}
    fire_style = "classic"
    debug_mode = False
    fullscreen = False
    window_name = "THE FIREBENDER AI"
    
    # FPS tracking
    prev_time = time.time()
    fps = 0

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1280, 720)

    print("✅ Ready! Show your hands to the camera.")

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("⚠ Camera frame error, retrying...")
            continue

        # Mirror the frame
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        # FPS calculation
        current_time = time.time()
        dt = current_time - prev_time
        fps = 1.0 / max(dt, 0.001)
        prev_time = current_time

        # Process hand detection
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        results = detector.detect(mp_image)

        # Slightly darken the frame for more dramatic fire effect
        frame = cv2.convertScaleAbs(frame, alpha=0.75, beta=-10)

        # Create fire layer (black background for additive blending)
        fire_layer = np.zeros_like(frame)

        # Get current palette
        palette = FIRE_PALETTES[fire_style]

        # ─── Process detected hands ───
        if results.hand_landmarks:
            for hand_idx, hand_lms in enumerate(results.hand_landmarks):
                
                # Calculate hand center
                cx = int(np.mean([lm.x for lm in hand_lms]) * w)
                cy = int(np.mean([lm.y for lm in hand_lms]) * h)

                # Track hand velocity
                hand_key = f"hand_{hand_idx}"
                prev_pos = prev_hand_positions.get(hand_key)
                velocity = calculate_hand_velocity((cx, cy), prev_pos, dt * 1000)
                prev_hand_positions[hand_key] = (cx, cy)

                # Count open fingers for intensity
                open_fingers = count_open_fingers(hand_lms, frame.shape)
                intensity = 0.5 + (open_fingers / 5.0) * 1.5  # 0.5 to 2.0
                
                # Velocity boost
                vel_boost = min(velocity * 0.02, 2.0)
                total_intensity = intensity + vel_boost

                # Draw subtle magic circle around hand
                circle_radius = int(80 * total_intensity)
                circle_alpha = min(0.2, total_intensity * 0.08)
                draw_magic_circle(frame, cx, cy, circle_radius, palette["glow"], circle_alpha)

                # ─── Spawn particles from each fingertip ───
                for tip_idx in FINGERTIPS:
                    lm = hand_lms[tip_idx]
                    fx, fy = int(lm.x * w), int(lm.y * h)

                    # Number of particles based on intensity
                    num_particles = int(PARTICLES_PER_FINGER * total_intensity)
                    
                    if len(particles) < MAX_PARTICLES:
                        for _ in range(num_particles):
                            particles.append(FireParticle(
                                fx, fy,
                                velocity_scale=total_intensity,
                                palette=fire_style
                            ))

                        # Ember sparks
                        if random.random() < EMBER_CHANCE * total_intensity:
                            particles.append(EmberParticle(fx, fy, palette=fire_style))

                        # Smoke wisps
                        if random.random() < SMOKE_CHANCE:
                            particles.append(SmokeParticle(fx, fy, palette=fire_style))

                # ─── Palm center fire burst ───
                if open_fingers >= 4:
                    palm_lm = hand_lms[9]  # Middle finger base (palm center)
                    px, py = int(palm_lm.x * w), int(palm_lm.y * h)
                    if len(particles) < MAX_PARTICLES:
                        for _ in range(3):
                            particles.append(FireParticle(
                                px, py,
                                velocity_scale=total_intensity * 0.7,
                                palette=fire_style
                            ))

        # ─── Update & draw all particles ───
        # Process smoke first (background), then fire, then embers (foreground)
        smoke_particles = []
        fire_particles = []
        ember_particles = []

        for p in particles:
            if isinstance(p, SmokeParticle):
                smoke_particles.append(p)
            elif isinstance(p, EmberParticle):
                ember_particles.append(p)
            else:
                fire_particles.append(p)

        # Draw smoke on frame directly (semi-transparent)
        for p in smoke_particles:
            p.update()
            if not p.is_dead:
                p.draw(frame, palette)

        # Draw fire on fire_layer (for glow effect)
        for p in fire_particles:
            p.update()
            if not p.is_dead:
                p.draw(fire_layer, palette)

        # Draw embers on fire_layer
        for p in ember_particles:
            p.update()
            if not p.is_dead:
                p.draw(fire_layer, palette)

        # Remove dead particles
        particles = [p for p in particles if not p.is_dead]

        # ─── Apply glow and composite ───
        if len(particles) > 0:
            frame = apply_glow_effect(frame, fire_layer, palette["glow"])

        # ─── Draw HUD ───
        draw_hud(frame, fps, len(particles), fire_style, debug_mode)

        # ─── Display ───
        cv2.imshow(window_name, frame)

        # ─── Keyboard controls ───
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:  # Q or ESC
            break
        elif key == ord('f'):
            fullscreen = not fullscreen
            if fullscreen:
                cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            else:
                cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
        elif key == ord('d'):
            debug_mode = not debug_mode
        elif key == ord('1'):
            fire_style = "classic"
            print("🔥 Style: Classic Fire")
        elif key == ord('2'):
            fire_style = "blue"
            print("💙 Style: Blue Flame")
        elif key == ord('3'):
            fire_style = "green"
            print("💚 Style: Green Inferno")

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    detector.close()
    print("\n🔥 Firebender AI terminated. See you next time!")


if __name__ == "__main__":
    main()
