import cv2
import numpy as np
import time

class TrafficLightDetector:
    def __init__(self, camera_index=0, debug=False):
        """
        Trafik ışığı tespit edici sınıf
        
        Args:
            camera_index (int): Kamera indeksi (varsayılan: 0)
            debug (bool): Hata ayıklama modunu etkinleştirir (varsayılan: False)
        """
        self.camera_index = camera_index
        self.debug = debug
        self.camera = None
        
        # Yeşil renk için HSV aralığı (bu değerler ayarlanabilir)
        self.lower_green = np.array([40, 50, 50])
        self.upper_green = np.array([90, 255, 255])
        
        # İlgi alanı (ROI) - trafik ışığının beklendiği bölge
        # Varsayılan olarak görüntünün üst orta kısmı
        self.roi_x = 0.25  # Görüntünün sol kenarından itibaren % olarak
        self.roi_width = 0.5  # Görüntü genişliğinin % olarak
        self.roi_y = 0  # Görüntünün üstünden itibaren % olarak
        self.roi_height = 0.3  # Görüntü yüksekliğinin % olarak
        
        # Yeşil ışık algılama parametreleri
        self.min_green_area = 100  # Minimum yeşil piksel alanı
        self.green_threshold = 0.05  # Yeşil alan eşik değeri (ROI'nin yüzdesi olarak)
        
    def start_camera(self):
        """Kamerayı başlatır"""
        self.camera = cv2.VideoCapture(self.camera_index)
        if not self.camera.isOpened():
            raise RuntimeError("Kamera başlatılamadı!")
        return self.camera.isOpened()
    
    def stop_camera(self):
        """Kamerayı durdurur"""
        if self.camera is not None:
            self.camera.release()
    
    def set_roi(self, x, y, width, height):
        """
        İlgi alanını (ROI) ayarlar
        
        Args:
            x (float): ROI'nin sol kenarının x koordinatı (0-1 arası)
            y (float): ROI'nin üst kenarının y koordinatı (0-1 arası)
            width (float): ROI genişliği (0-1 arası)
            height (float): ROI yüksekliği (0-1 arası)
        """
        self.roi_x = max(0, min(1, x))
        self.roi_y = max(0, min(1, y))
        self.roi_width = max(0, min(1, width))
        self.roi_height = max(0, min(1, height))
    
    def set_green_threshold(self, threshold):
        """
        Yeşil ışık algılama eşik değerini ayarlar
        
        Args:
            threshold (float): Yeşil alan eşik değeri (0-1 arası)
        """
        self.green_threshold = max(0, min(1, threshold))
    
    def set_hsv_range(self, lower_green, upper_green):
        """
        Yeşil renk için HSV aralığını ayarlar
        
        Args:
            lower_green (np.array): Alt HSV değerleri [H, S, V]
            upper_green (np.array): Üst HSV değerleri [H, S, V]
        """
        self.lower_green = np.array(lower_green)
        self.upper_green = np.array(upper_green)
    
    def detect_green_light(self, frame=None):
        """
        Görüntüde yeşil trafik ışığını tespit eder
        
        Args:
            frame (np.array, optional): İşlenecek görüntü. None ise kameradan alınır.
            
        Returns:
            bool: Yeşil ışık tespit edilirse True, aksi halde False
            dict: Tespit sonuçları hakkında ek bilgiler
        """
        if frame is None:
            if self.camera is None:
                self.start_camera()
            
            ret, frame = self.camera.read()
            if not ret:
                return False, {"error": "Kameradan görüntü alınamadı"}
        
        # Görüntü boyutlarını al
        height, width = frame.shape[:2]
        
        # ROI koordinatlarını hesapla
        roi_x1 = int(width * self.roi_x)
        roi_y1 = int(height * self.roi_y)
        roi_x2 = int(roi_x1 + width * self.roi_width)
        roi_y2 = int(roi_y1 + height * self.roi_height)
        
        # ROI'yi kes
        roi = frame[roi_y1:roi_y2, roi_x1:roi_x2]
        
        # HSV'ye dönüştür
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        
        # Yeşil renk maskesi oluştur
        mask = cv2.inRange(hsv, self.lower_green, self.upper_green)
        
        # Gürültüyü azaltmak için morfolojik işlemler
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.erode(mask, kernel, iterations=1)
        mask = cv2.dilate(mask, kernel, iterations=2)
        
        # Yeşil piksellerin sayısını hesapla
        green_pixel_count = cv2.countNonZero(mask)
        total_roi_pixels = roi.shape[0] * roi.shape[1]
        green_ratio = green_pixel_count / total_roi_pixels if total_roi_pixels > 0 else 0
        
        # Yeşil ışık tespit edildi mi?
        is_green_light = green_pixel_count > self.min_green_area and green_ratio > self.green_threshold
        
        # Debug modunda görselleştirme
        if self.debug:
            # ROI'yi çiz
            debug_frame = frame.copy()
            cv2.rectangle(debug_frame, (roi_x1, roi_y1), (roi_x2, roi_y2), (0, 255, 0), 2)
            
            # Maskeyi renkli görüntüye dönüştür
            mask_colored = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
            
            # Sonuç metni
            text = "YESIL ISIK TESPIT EDILDI" if is_green_light else "YESIL ISIK YOK"
            color = (0, 255, 0) if is_green_light else (0, 0, 255)
            cv2.putText(debug_frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
            cv2.putText(debug_frame, f"Yesil Oran: {green_ratio:.4f}", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Görüntüleri göster
            cv2.imshow("Orijinal Goruntu", debug_frame)
            cv2.imshow("ROI", roi)
            cv2.imshow("Yesil Maske", mask_colored)
            cv2.waitKey(1)
        
        return is_green_light, {
            "green_pixel_count": green_pixel_count,
            "total_roi_pixels": total_roi_pixels,
            "green_ratio": green_ratio,
            "roi": (roi_x1, roi_y1, roi_x2, roi_y2)
        }
    
    def wait_for_green_light(self, timeout=None):
        """
        Yeşil ışık tespit edilene kadar bekler
        
        Args:
            timeout (float, optional): Maksimum bekleme süresi (saniye). None ise süresiz bekler.
            
        Returns:
            bool: Yeşil ışık tespit edilirse True, zaman aşımı olursa False
        """
        if self.camera is None:
            self.start_camera()
        
        start_time = time.time()
        
        while True:
            is_green, _ = self.detect_green_light()
            
            if is_green:
                return True
            
            if timeout is not None and (time.time() - start_time) > timeout:
                return False
            
            # CPU yükünü azaltmak için kısa bir bekleme
            time.sleep(0.05)


def main():
    """Test fonksiyonu"""
    detector = TrafficLightDetector(camera_index=0, debug=True)
    
    try:
        print("Trafik ışığı tespit ediliyor...")
        print("Yeşil ışık için bekleniyor...")
        print("Çıkmak için 'q' tuşuna basın")
        
        detector.start_camera()
        
        while True:
            is_green, info = detector.detect_green_light()
            
            if is_green:
                print("YEŞİL IŞIK TESPİT EDİLDİ!")
            
            # 'q' tuşuna basılırsa çık
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("Program kullanıcı tarafından durduruldu")
    finally:
        detector.stop_camera()
        cv2.destroyAllWindows()
        print("Program sonlandırıldı")


if __name__ == "__main__":
    main() 