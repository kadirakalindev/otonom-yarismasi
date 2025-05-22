import time
import cv2
import numpy as np
import argparse
import os
import sys
from traffic_light_detection import TrafficLightDetector
from motor_control import MotorController

def parse_arguments():
    """Komut satırı argümanlarını ayrıştırır"""
    parser = argparse.ArgumentParser(description="Otonom Araç Kontrol Programı")
    parser.add_argument("--camera", type=int, default=0, help="Kamera indeksi")
    parser.add_argument("--debug", action="store_true", help="Hata ayıklama modunu etkinleştirir")
    parser.add_argument("--test-mode", choices=["traffic_light", "motor", "all"], 
                        default="all", help="Test modu seçimi")
    return parser.parse_args()

def main():
    """Ana program"""
    args = parse_arguments()
    
    print("Otonom Araç Kontrol Programı başlatılıyor...")
    
    # Trafik ışığı detektörünü başlat
    detector = TrafficLightDetector(camera_index=args.camera, debug=args.debug)
    
    # Motor kontrolcüsünü başlat
    motor = MotorController(
        left_motor_pins=(16, 18),
        right_motor_pins=(36, 38),
        left_pwm_pin=12,
        right_pwm_pin=32
    )
    
    try:
        if args.test_mode == "traffic_light":
            test_traffic_light(detector)
        elif args.test_mode == "motor":
            test_motor(motor)
        else:
            run_autonomous_mode(detector, motor)
            
    except KeyboardInterrupt:
        print("Program kullanıcı tarafından durduruldu")
    finally:
        motor.cleanup()
        detector.stop_camera()
        cv2.destroyAllWindows()
        print("Program sonlandırıldı")

def test_traffic_light(detector):
    """Trafik ışığı tanıma testini çalıştırır"""
    print("Trafik ışığı testi başlatılıyor...")
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

def test_motor(motor):
    """Motor kontrol testini çalıştırır"""
    print("Motor testi başlatılıyor...")
    
    # İleri git
    print("İleri gidiliyor...")
    motor.forward(0.5)
    time.sleep(2)
    
    # Dur
    print("Durduruluyor...")
    motor.stop()
    time.sleep(1)
    
    # Sola dön
    print("Sola dönülüyor...")
    motor.turn_left(0.5)
    time.sleep(2)
    
    # Dur
    motor.stop()
    time.sleep(1)
    
    # Sağa dön
    print("Sağa dönülüyor...")
    motor.turn_right(0.5)
    time.sleep(2)
    
    # Dur
    motor.stop()
    time.sleep(1)
    
    # Yerinde sola dön
    print("Yerinde sola dönülüyor...")
    motor.rotate_left(0.5)
    time.sleep(2)
    
    # Dur
    motor.stop()
    time.sleep(1)
    
    # Yerinde sağa dön
    print("Yerinde sağa dönülüyor...")
    motor.rotate_right(0.5)
    time.sleep(2)
    
    # Dur
    motor.stop()

def run_autonomous_mode(detector, motor):
    """Otonom sürüş modunu çalıştırır"""
    print("Otonom sürüş modu başlatılıyor...")
    print("Yeşil ışık için bekleniyor...")
    print("Çıkmak için 'q' tuşuna basın")
    
    detector.start_camera()
    
    # Durum makinesi değişkenleri
    state = "WAITING_FOR_GREEN"
    green_light_detected = False
    
    while True:
        # Kameradan görüntü al
        ret, frame = detector.camera.read()
        if not ret:
            print("Kameradan görüntü alınamadı!")
            break
        
        # Durum makinesine göre işlem yap
        if state == "WAITING_FOR_GREEN":
            is_green, info = detector.detect_green_light(frame)
            
            if is_green and not green_light_detected:
                print("YEŞİL IŞIK TESPİT EDİLDİ! Araç hareket ediyor...")
                green_light_detected = True
                state = "MOVING"
                motor.forward(0.5)  # %50 hızla ileri git
        
        elif state == "MOVING":
            # Burada şerit takibi, engel tespiti vb. işlemler eklenecek
            pass
        
        # 'q' tuşuna basılırsa çık
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


if __name__ == "__main__":
    main() 