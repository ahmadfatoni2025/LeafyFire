import cv2
import time
import math
import numpy as np
import config
from hand_tracker import HandTracker
from fire_effect import FluidFire

def count_open_fingers(hand_lms):
    """Menghitung berapa banyak jari yang sedang terbuka berdasarkan jaraknya dari pergelangan tangan"""
    open_fingers = 0
    wrist = hand_lms[0]
    
    # Indeks ujung jari dan pangkal sendi
    # (Telunjuk: 8 vs 5), (Tengah: 12 vs 9), (Manis: 16 vs 13), (Kelingking: 20 vs 17)
    for tip, joint in [(8, 5), (12, 9), (16, 13), (20, 17)]:
        dist_tip = ((hand_lms[tip].x - wrist.x)**2 + (hand_lms[tip].y - wrist.y)**2)
        dist_joint = ((hand_lms[joint].x - wrist.x)**2 + (hand_lms[joint].y - wrist.y)**2)
        
        # Jika jarak ujung jari ke pergelangan lebih jauh dari pada sendi = terbuka
        if dist_tip > dist_joint * 1.2:
            open_fingers += 1
            
    # Jempol unik karena menyamping
    dist_thumb_tip = ((hand_lms[4].x - wrist.x)**2 + (hand_lms[4].y - wrist.y)**2)
    dist_thumb_base = ((hand_lms[2].x - wrist.x)**2 + (hand_lms[2].y - wrist.y)**2)
    if dist_thumb_tip > dist_thumb_base * 1.5:
        open_fingers += 1
        
    return open_fingers

def main():
    print("Membuka kamera...")
    cap = cv2.VideoCapture(config.CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)

    # Inisialisasi Detektor Tangan
    tracker = HandTracker()
    
    success, frame = cap.read()
    if not success:
        print("Kamera tidak dapat diakses.")
        return
    
    # Ambil resolusi riil dari kamera (jaga-jaga jika kamera tidak mendukung 640x480)
    h, w = frame.shape[:2]
    
    # Inisialisasi modul Api
    # Resolusi api dibuat dinamis menyesuaikan layar
    fire = FluidFire(w, h, colormap='classic')

    prev_time = time.time()
    color_styles = ['classic', 'blue', 'green']
    color_idx = 0

    # Variabel State untuk Ultimate Skill (Iron Man Effect)
    charge_level = 0
    is_charging = False
    flash_intensity = 0
    center_x, center_y = 0, 0

    print("🔥 THE FIREBENDER AI - Fluid Edition 🔥")
    print("========================================")
    print("1. Efek partikel dihapus, diganti menggunakan Heat Matrix (Jauh lebih ringan)")
    print("2. Terlihat lebih menyatu ibarat sihir di film")
    print("3. Kode telah dibagi menjadi file: main, config, hand_tracker, fire_effect")
    print("Controls:")
    print("  (C) : Ubah warna api")
    print("  (Q) : Keluar")
    print("========================================")

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        # Efek cermin
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 1. Deteksi tangan
        results = tracker.process(rgb_frame)

        # 2. Update koordinat panas berdasarkan ujung jari
        if results.hand_landmarks:
            num_hands = len(results.hand_landmarks)
            hand_distance = 999.0
            
            # --- [FITUR BARU] IRON MAN ULTIMATE CHARGE ---
            if num_hands == 2:
                # Ambil pangkal jari tengah kedua tangan untuk mengukur jarak
                h1 = results.hand_landmarks[0][9]
                h2 = results.hand_landmarks[1][9]
                dx, dy = h1.x - h2.x, h1.y - h2.y
                hand_distance = math.sqrt(dx*dx + dy*dy)
                
                center_x = int(((h1.x + h2.x) / 2) * w)
                center_y = int(((h1.y + h2.y) / 2) * h)

            # Aturan fisika Ultimate
            # Jika tangan berdekatan (jarak < 0.15) maka akan memusatkan energi
            if num_hands == 2 and hand_distance < 0.15:
                is_charging = True
                charge_level = min(charge_level + 4, 200) # Max 200
                
                # Simulasi energi yang mengumpul
                radius_charge = int(25 + (charge_level * 0.4))
                fire.add_heat(center_x, center_y, radius=radius_charge, intensity=250)
                
            elif is_charging and hand_distance > 0.3:
                # Tangan dibuka lebar setelah di charge (BOOM!)
                if charge_level > 50:
                    boom_radius = int(80 + charge_level * 1.2)
                    fire.add_heat(center_x, center_y, radius=boom_radius, intensity=255) # Tambahkan efek sangat panas
                    flash_intensity = min(charge_level * 2, 255) # White flash
                # Reset
                is_charging = False
                charge_level = 0
            else:
                if hand_distance > 0.18:
                    is_charging = False
                    charge_level = max(charge_level - 10, 0)
            # ---------------------------------------------
            
            for hand_lms in results.hand_landmarks:
                
                # Cek apakah tangan sedang terbuka atau mengepal
                open_fingers = count_open_fingers(hand_lms)
                
                if open_fingers >= 2:
                    # Ujung jari telunjuk, tengah, manis, dll
                    # Hanya tambahkan panas ke jari yang terbuka (simpelnya kita spawn ke semua jari & palm)
                    for tip_idx in [4, 8, 12, 16, 20]:
                        x = int(hand_lms[tip_idx].x * w)
                        y = int(hand_lms[tip_idx].y * h)
                        
                        # Tambahkan titik panas di kordinat tangan tersebut
                        # Membuat jilatan api terlihat lebih kecil & menyambung
                        fire.add_heat(x, y, radius=15, intensity=255)
                    
                    # Telapak tangan (Basis utama letupan api)
                    px = int(hand_lms[9].x * w)
                    py = int(hand_lms[9].y * h)
                    fire.add_heat(px, py, radius=40, intensity=230)

        # 3. Proses matrix fisika fluida (update posisi api yang tersebar)
        fire.update()
        
        # Dapatkan gambar/grafis final api tersebut
        fire_overlay = fire.get_fire_overlay(frame.shape)

        # 4. Filter & Blending
        # Gelapkan layar agar efek api lebih terlihat natural / glowing
        darkened_frame = cv2.convertScaleAbs(frame, alpha=0.5, beta=-15)
        
        # Mode Penjumlahan/Screen/Additive (Tumpuk frame asli dengan overlay api yang terang)
        # Gunakan addWeighted dengan bobot sedikit lebih besar agar api sangat terang
        final_frame = cv2.addWeighted(darkened_frame, 1.0, fire_overlay, 1.2, 0)
        
        # --- UI EFFECTS (Iron Man Hologram & Explosion Flash) ---
        if is_charging and charge_level > 10:
            # Gambar elemen VR melingkar
            ring_color = (0, 200, 255) if color_idx == 0 else (255, 100, 0) if color_idx == 1 else (50, 255, 50)
            cv2.circle(final_frame, (center_x, center_y), charge_level + 20, ring_color, 2, cv2.LINE_AA)
            cv2.circle(final_frame, (center_x, center_y), int(charge_level * 0.5) + 5, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(final_frame, f"ENERGY: {charge_level}%", (center_x - 50, center_y - charge_level - 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, ring_color, 2)
                        
        if flash_intensity > 0:
            # Aplikasikan layar yang sepenuhnya putih dari sisa flash efek ledakan
            flash_overlay = np.full_like(final_frame, (255, 255, 255))
            alpha = flash_intensity / 255.0
            final_frame = cv2.addWeighted(final_frame, 1.0 - alpha, flash_overlay, alpha, 0)
            flash_intensity -= 15 # Turunkan nilai secara periodik

        # 5. UI Status System
        curr_time = time.time()
        fps = 1 / max(curr_time - prev_time, 0.001)
        prev_time = curr_time
        
        cv2.putText(final_frame, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(final_frame, f"Style: {color_styles[color_idx].upper()} (Tekan 'C' di keyboard)", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

        cv2.imshow("Firebender AI - Fluid Edition", final_frame)

        # Keyboard Interaktif
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            color_idx = (color_idx + 1) % len(color_styles)
            fire.set_colormap(color_styles[color_idx])

    # Hapus semua pada memori
    cap.release()
    cv2.destroyAllWindows()
    tracker.close()

if __name__ == "__main__":
    main()
