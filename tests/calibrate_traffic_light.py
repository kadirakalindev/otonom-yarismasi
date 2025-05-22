import cv2
import numpy as np
import argparse
import sys
import os

# Ana dizini import path'e ekle
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def nothing(x):
    """Trackbar callback fonksiyonu"""
    pass

def main():
    """
    Trafik ışığı tanıma için HSV değerlerini kalibre etme aracı.
    Bu program, yeşil renk için HSV aralığını interaktif olarak ayarlamanıza olanak tanır.
    """
    parser = argparse.ArgumentParser(description="HSV Renk Kalibrasyonu")
    parser.add_argument("--camera", type=int, default=0, help="Kamera indeksi")
    args = parser.parse_args()
    
    # Kamerayı başlat
    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        print("Kamera açılamadı!")
        return
    
    # Pencere oluştur
    cv2.namedWindow('HSV Ayarlari')
    cv2.namedWindow('Orijinal')
    cv2.namedWindow('Maske')
    
    # Trackbar'ları oluştur
    cv2.createTrackbar('H Min', 'HSV Ayarlari', 40, 179, nothing)
    cv2.createTrackbar('H Max', 'HSV Ayarlari', 90, 179, nothing)
    cv2.createTrackbar('S Min', 'HSV Ayarlari', 50, 255, nothing)
    cv2.createTrackbar('S Max', 'HSV Ayarlari', 255, 255, nothing)
    cv2.createTrackbar('V Min', 'HSV Ayarlari', 50, 255, nothing)
    cv2.createTrackbar('V Max', 'HSV Ayarlari', 255, 255, nothing)
    
    # ROI için trackbar'lar
    cv2.createTrackbar('ROI X', 'HSV Ayarlari', 25, 100, nothing)  # % olarak
    cv2.createTrackbar('ROI Y', 'HSV Ayarlari', 0, 100, nothing)   # % olarak
    cv2.createTrackbar('ROI Width', 'HSV Ayarlari', 50, 100, nothing)  # % olarak
    cv2.createTrackbar('ROI Height', 'HSV Ayarlari', 30, 100, nothing)  # % olarak
    
    print("HSV değerlerini ayarlamak için trackbar'ları kullanın.")
    print("Çıkmak için 'q' tuşuna basın.")
    print("Ayarları kaydetmek için 's' tuşuna basın.")
    
    while True:
        # Kameradan görüntü al
        ret, frame = cap.read()
        if not ret:
            print("Görüntü alınamadı!")
            break
        
        # Trackbar değerlerini al
        h_min = cv2.getTrackbarPos('H Min', 'HSV Ayarlari')
        h_max = cv2.getTrackbarPos('H Max', 'HSV Ayarlari')
        s_min = cv2.getTrackbarPos('S Min', 'HSV Ayarlari')
        s_max = cv2.getTrackbarPos('S Max', 'HSV Ayarlari')
        v_min = cv2.getTrackbarPos('V Min', 'HSV Ayarlari')
        v_max = cv2.getTrackbarPos('V Max', 'HSV Ayarlari')
        
        # ROI trackbar değerlerini al
        roi_x = cv2.getTrackbarPos('ROI X', 'HSV Ayarlari') / 100.0
        roi_y = cv2.getTrackbarPos('ROI Y', 'HSV Ayarlari') / 100.0
        roi_width = cv2.getTrackbarPos('ROI Width', 'HSV Ayarlari') / 100.0
        roi_height = cv2.getTrackbarPos('ROI Height', 'HSV Ayarlari') / 100.0
        
        # ROI koordinatlarını hesapla
        height, width = frame.shape[:2]
        roi_x1 = int(width * roi_x)
        roi_y1 = int(height * roi_y)
        roi_x2 = int(roi_x1 + width * roi_width)
        roi_y2 = int(roi_y1 + height * roi_height)
        
        # ROI'yi çiz
        frame_with_roi = frame.copy()
        cv2.rectangle(frame_with_roi, (roi_x1, roi_y1), (roi_x2, roi_y2), (0, 255, 0), 2)
        
        # ROI'yi kes
        roi = frame[roi_y1:roi_y2, roi_x1:roi_x2]
        
        # HSV'ye dönüştür
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        
        # HSV aralığını belirle
        lower_green = np.array([h_min, s_min, v_min])
        upper_green = np.array([h_max, s_max, v_max])
        
        # Maske oluştur
        mask = cv2.inRange(hsv, lower_green, upper_green)
        
        # Gürültüyü azaltmak için morfolojik işlemler
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.erode(mask, kernel, iterations=1)
        mask = cv2.dilate(mask, kernel, iterations=2)
        
        # Yeşil piksellerin sayısını hesapla
        green_pixel_count = cv2.countNonZero(mask)
        total_roi_pixels = roi.shape[0] * roi.shape[1]
        green_ratio = green_pixel_count / total_roi_pixels if total_roi_pixels > 0 else 0
        
        # Sonuç metnini hazırla
        hsv_text = f"HSV Min: [{h_min}, {s_min}, {v_min}], Max: [{h_max}, {s_max}, {v_max}]"
        ratio_text = f"Yesil Oran: {green_ratio:.4f}, Piksel: {green_pixel_count}/{total_roi_pixels}"
        
        # Sonuç metnini görüntüye ekle
        cv2.putText(frame_with_roi, hsv_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame_with_roi, ratio_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Maskeyi renkli görüntüye dönüştür (görselleştirme için)
        mask_colored = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        
        # Görüntüleri göster
        cv2.imshow('Orijinal', frame_with_roi)
        cv2.imshow('ROI', roi)
        cv2.imshow('Maske', mask_colored)
        
        # Tuş kontrolü
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            # Ayarları kaydet
            config = {
                'hsv_min': [h_min, s_min, v_min],
                'hsv_max': [h_max, s_max, v_max],
                'roi': [roi_x, roi_y, roi_width, roi_height]
            }
            save_config(config)
            print("Ayarlar kaydedildi!")
    
    # Temizlik
    cap.release()
    cv2.destroyAllWindows()

def save_config(config):
    """
    Kalibrasyon ayarlarını bir dosyaya kaydeder
    
    Args:
        config (dict): Kalibrasyon ayarları
    """
    # Ana dizindeki config dosyasına kaydet
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'traffic_light_config.py'))
    
    with open(config_path, 'w') as f:
        f.write("# Trafik ışığı tanıma için kalibrasyon ayarları\n\n")
        f.write(f"HSV_MIN = {config['hsv_min']}\n")
        f.write(f"HSV_MAX = {config['hsv_max']}\n")
        f.write(f"ROI = {config['roi']}\n")
        f.write("\n# Kullanım örneği:\n")
        f.write("# from traffic_light_config import HSV_MIN, HSV_MAX, ROI\n")
        f.write("# detector.set_hsv_range(HSV_MIN, HSV_MAX)\n")
        f.write("# detector.set_roi(ROI[0], ROI[1], ROI[2], ROI[3])\n")

if __name__ == "__main__":
    main() 