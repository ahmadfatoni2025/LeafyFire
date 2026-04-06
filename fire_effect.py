import cv2
import numpy as np
import config

class FluidFire:
    def __init__(self, width, height, colormap='classic'):
        """
        Sistem visualisasi api berbasis matriks aliran fluida/panas.
        Ini jauh lebih efisien & ringan daripada membuat partikel individu (Class Particle).
        """
        # Downscale resolusi untuk rendering agar super ringan & cepat
        self.scale = config.FIRE_SCALE
        self.w = int(width * self.scale)
        self.h = int(height * self.scale)
        
        # Buffer untuk menyimpan intensitas 'panas' dari api (Hitam = 0, Putih/Max = 255)
        self.heat_buffer = np.zeros((self.h, self.w), dtype=np.uint8)
        self.tick = 0
        self.custom_colormap = self.create_fire_colormap()
        self.set_colormap(colormap)

    def create_fire_colormap(self):
        """Membuat palet warna api ultra-realistis yang sesuai dengan gambar referensi"""
        colormap = np.zeros((256, 1, 3), dtype=np.uint8)
        for i in range(256):
            if i < 40:
                # Hitam ke Merah Gelap pekat
                r = int((i / 40.0) * 80)
                colormap[i, 0, :] = [0, 0, r]    # [B, G, R]
            elif i < 110:
                # Merah Gelap ke Merah-Oranye terang
                p = (i - 40) / 70.0
                r = int(80 + p * 175)
                g = int(p * 80)
                colormap[i, 0, :] = [0, g, r]
            elif i < 180:
                # Oranye ke Kuning
                p = (i - 110) / 70.0
                r = 255
                g = int(80 + p * 120)
                colormap[i, 0, :] = [0, g, r]
            elif i < 240:
                # Kuning ke Kuning Terang
                p = (i - 180) / 60.0
                r = 255
                g = int(200 + p * 55)
                b = int(p * 150)
                colormap[i, 0, :] = [b, g, r]
            else:
                # Putih (inti api/sumber terpanas)
                p = (i - 240) / 15.0
                r = 255
                g = 255
                b = int(150 + p * 105)
                colormap[i, 0, :] = [b, g, r]
        return colormap

    def set_colormap(self, style):
        self.style = style

    def apply_color(self, heat):
        """Memetakan nilai panas (0-255) menjadi warna gradient yang realistis"""
        if self.style == 'blue':
            return cv2.applyColorMap(heat, cv2.COLORMAP_OCEAN)
        elif self.style == 'green':
            color = cv2.applyColorMap(heat, cv2.COLORMAP_SUMMER)
            color[heat < 10] = [0, 0, 0]
            return color
        else:
            # Gunakan Palet Ultra-Realistis
            return cv2.applyColorMap(heat, self.custom_colormap)

    def add_heat(self, x, y, radius=15, intensity=255):
        """Menambahkan 'sumber panas' pada kordinat tertentu (biasanya di ujung jari)"""
        # Sesuaikan dengan skala downscale
        sx, sy = int(x * self.scale), int(y * self.scale)
        if 0 <= sx < self.w and 0 <= sy < self.h:
            # Gunakan radius yang disesuaikan & gambar sirkulasi panas
            scaled_radius = int(radius * self.scale)
            cv2.circle(self.heat_buffer, (sx, sy), scaled_radius, intensity, -1)

    def update(self):
        """Siklus Fisika: Panas naik ke atas, mendingin, lalu menyebar"""
        shift_y = int(8 * self.scale) + 1  # Kecepatan dasar api mengalir
        self.tick += 1
        
        # 1. Turbulensi & Distorsi (Membuat api melmeliuk seperti di dunia nyata)
        # Efek pergerakan melengkung (kiri-kanan) berdasarkan gelombang sinus
        shift_x = int(np.sin(self.tick * 0.15) * 3 * self.scale)
        
        new_buffer = np.zeros_like(self.heat_buffer)
        
        # Geser ke atas
        temp_buffer = np.zeros_like(self.heat_buffer)
        temp_buffer[:-shift_y, :] = self.heat_buffer[shift_y:, :]
        
        # Gelombang kesamping
        if shift_x > 0:
            new_buffer[:, shift_x:] = temp_buffer[:, :-shift_x]
        elif shift_x < 0:
            new_buffer[:, :shift_x] = temp_buffer[:, -shift_x:]
        else:
            new_buffer = temp_buffer.copy()
            
        # Distorsi mikro (turbulensi pinggiran api)
        new_buffer = cv2.GaussianBlur(new_buffer, (5, 7), 0) # Anisotropic blur (merenggang ke atas)

        # 2. Kurangi intensitas / mendingin (Cooling effect) 
        # Kita memperlambat cooling agar lidah apinya panjang ke atas
        new_buffer = cv2.addWeighted(new_buffer, 0.94, new_buffer, 0, -1)
        
        self.heat_buffer = new_buffer

    def get_fire_overlay(self, frame_shape):
        """Warnai heat buffer dan kembalikan overlay yang siap di-tumpuk ke frame asli"""
        
        # Dapatkan warna gradasi dari panas
        colored_fire = self.apply_color(self.heat_buffer)
        
        # Potong area gelap gulita (masking)
        mask = (self.heat_buffer > 8).astype(np.uint8)
        colored_fire = cv2.bitwise_and(colored_fire, colored_fire, mask=mask)
        
        # Kembalikan ukurannya menjadi sebesar ukuran frame kamera asli
        colored_fire_resized = cv2.resize(
            colored_fire, 
            (frame_shape[1], frame_shape[0]), 
            interpolation=cv2.INTER_LINEAR
        )
        
        return colored_fire_resized
