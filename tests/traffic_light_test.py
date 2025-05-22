import time
import cv2
import sys
import os

# Ana dizini import path'e ekle
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from traffic_light_detection import TrafficLightDetector
from motor_control import MotorController

def main():
    """
    Trafik ışığı tanıma ve motor kontrolü için test programı.
    Yeşil ışık algılandığında araç hareket edecek.
    """
    print("Trafik ışığı test programı başlatılıyor...")
    
    # Trafik ışığı detektörünü başlat
    detector = TrafficLightDetector(camera_index=0, debug=True)
    
    # Motor kontrolcüsünü başlat
    motor = MotorController(
        left_motor_pins=(16, 18),
        right_motor_pins=(36, 38),
        left_pwm_pin=12,
        right_pwm_pin=32
    )
    
    try:
        print("Yeşil ışık için bekleniyor...")
        print("Çıkmak için 'q' tuşuna basın")
        
        detector.start_camera()
        
        # Yeşil ışık algılanana kadar bekle
        green_light_detected = False
        
        while True:
            is_green, info = detector.detect_green_light()
            
            # Yeşil ışık algılandıysa ve daha önce algılanmadıysa
            if is_green and not green_light_detected:
                print("YEŞİL IŞIK TESPİT EDİLDİ! Araç hareket ediyor...")
                green_light_detected = True
                
                # Aracı hareket ettir
                motor.forward(0.5)  # %50 hızla ileri git
                time.sleep(3)       # 3 saniye boyunca hareket et
                motor.stop()        # Dur
                
                print("Araç durdu. Tekrar yeşil ışık bekleniyor...")
                green_light_detected = False  # Tekrar yeşil ışık algılamaya hazır
            
            # 'q' tuşuna basılırsa çık
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("Program kullanıcı tarafından durduruldu")
    finally:
        motor.cleanup()
        detector.stop_camera()
        cv2.destroyAllWindows()
        print("Program sonlandırıldı")


if __name__ == "__main__":
    main() 