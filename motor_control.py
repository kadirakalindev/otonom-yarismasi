from gpiozero import DigitalOutputDevice, PWMOutputDevice
import time

class MotorController:
    def __init__(self, 
                 left_motor_pins=(16, 18),    # Sol motor için (IN1, IN2) pin numaraları
                 right_motor_pins=(36, 38),   # Sağ motor için (IN1, IN2) pin numaraları
                 left_pwm_pin=12,             # Sol motor için PWM enable pini
                 right_pwm_pin=32,            # Sağ motor için PWM enable pini
                 frequency=100):              # PWM frekansı
        """
        Motor kontrol sınıfı
        
        Args:
            left_motor_pins (tuple): Sol motor için (IN1, IN2) pin numaraları
            right_motor_pins (tuple): Sağ motor için (IN1, IN2) pin numaraları
            left_pwm_pin (int): Sol motor için PWM enable pini
            right_pwm_pin (int): Sağ motor için PWM enable pini
            frequency (int): PWM frekansı (Hz)
        """
        # Sol motor kontrol pinleri
        self.left_forward = DigitalOutputDevice(left_motor_pins[0])
        self.left_backward = DigitalOutputDevice(left_motor_pins[1])
        self.left_pwm = PWMOutputDevice(left_pwm_pin, frequency=frequency)
        
        # Sağ motor kontrol pinleri
        self.right_forward = DigitalOutputDevice(right_motor_pins[0])
        self.right_backward = DigitalOutputDevice(right_motor_pins[1])
        self.right_pwm = PWMOutputDevice(right_pwm_pin, frequency=frequency)
        
        # Başlangıçta motorları durdur
        self.stop()
        
    def set_left_motor(self, speed):
        """
        Sol motor hızını ve yönünü ayarlar
        
        Args:
            speed (float): Motor hızı ve yönü (-1.0 ile 1.0 arasında)
                          Pozitif değerler ileri, negatif değerler geri
        """
        speed = max(-1.0, min(1.0, speed))  # Hızı -1 ile 1 arasında sınırla
        
        if speed > 0:  # İleri
            self.left_forward.on()
            self.left_backward.off()
            self.left_pwm.value = speed
        elif speed < 0:  # Geri
            self.left_forward.off()
            self.left_backward.on()
            self.left_pwm.value = -speed
        else:  # Dur
            self.left_forward.off()
            self.left_backward.off()
            self.left_pwm.value = 0
    
    def set_right_motor(self, speed):
        """
        Sağ motor hızını ve yönünü ayarlar
        
        Args:
            speed (float): Motor hızı ve yönü (-1.0 ile 1.0 arasında)
                          Pozitif değerler ileri, negatif değerler geri
        """
        speed = max(-1.0, min(1.0, speed))  # Hızı -1 ile 1 arasında sınırla
        
        if speed > 0:  # İleri
            self.right_forward.on()
            self.right_backward.off()
            self.right_pwm.value = speed
        elif speed < 0:  # Geri
            self.right_forward.off()
            self.right_backward.on()
            self.right_pwm.value = -speed
        else:  # Dur
            self.right_forward.off()
            self.right_backward.off()
            self.right_pwm.value = 0
    
    def set_motors(self, left_speed, right_speed):
        """
        Her iki motorun hızını ve yönünü ayarlar
        
        Args:
            left_speed (float): Sol motor hızı ve yönü (-1.0 ile 1.0 arasında)
            right_speed (float): Sağ motor hızı ve yönü (-1.0 ile 1.0 arasında)
        """
        self.set_left_motor(left_speed)
        self.set_right_motor(right_speed)
    
    def forward(self, speed=1.0):
        """
        Aracı ileri hareket ettirir
        
        Args:
            speed (float): Hız (0.0 ile 1.0 arasında)
        """
        speed = max(0.0, min(1.0, speed))
        self.set_motors(speed, speed)
    
    def backward(self, speed=1.0):
        """
        Aracı geri hareket ettirir
        
        Args:
            speed (float): Hız (0.0 ile 1.0 arasında)
        """
        speed = max(0.0, min(1.0, speed))
        self.set_motors(-speed, -speed)
    
    def turn_left(self, speed=0.5):
        """
        Aracı sola döndürür
        
        Args:
            speed (float): Dönüş hızı (0.0 ile 1.0 arasında)
        """
        speed = max(0.0, min(1.0, speed))
        self.set_motors(0, speed)
    
    def turn_right(self, speed=0.5):
        """
        Aracı sağa döndürür
        
        Args:
            speed (float): Dönüş hızı (0.0 ile 1.0 arasında)
        """
        speed = max(0.0, min(1.0, speed))
        self.set_motors(speed, 0)
    
    def rotate_left(self, speed=0.5):
        """
        Aracı yerinde sola döndürür
        
        Args:
            speed (float): Dönüş hızı (0.0 ile 1.0 arasında)
        """
        speed = max(0.0, min(1.0, speed))
        self.set_motors(-speed, speed)
    
    def rotate_right(self, speed=0.5):
        """
        Aracı yerinde sağa döndürür
        
        Args:
            speed (float): Dönüş hızı (0.0 ile 1.0 arasında)
        """
        speed = max(0.0, min(1.0, speed))
        self.set_motors(speed, -speed)
    
    def stop(self):
        """Aracı durdurur"""
        self.set_motors(0, 0)
    
    def cleanup(self):
        """GPIO pinlerini temizler"""
        self.stop()
        self.left_pwm.close()
        self.right_pwm.close()
        self.left_forward.close()
        self.left_backward.close()
        self.right_forward.close()
        self.right_backward.close()


def main():
    """Test fonksiyonu"""
    # Varsayılan pin numaralarıyla motor kontrolcüsü oluştur
    motor = MotorController(
        left_motor_pins=(16, 18),
        right_motor_pins=(36, 38),
        left_pwm_pin=12,
        right_pwm_pin=32
    )
    
    try:
        print("Motor testi başlıyor...")
        
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
        
    except KeyboardInterrupt:
        print("Program kullanıcı tarafından durduruldu")
    finally:
        motor.cleanup()
        print("Motor kontrolü sonlandırıldı")


if __name__ == "__main__":
    main() 