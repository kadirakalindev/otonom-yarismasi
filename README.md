# Otonom Araç Projesi

Bu proje, Raspberry Pi 5 ve Raspberry Pi Camera 3 kullanarak geliştirilen bir otonom araç uygulamasıdır. Araç, trafik ışıklarını algılayıp, şeritleri takip ederek pist üzerinde hareket eder, engelleri aşar ve park alanına park eder.

## Özellikler

- Trafik ışığı algılama ve yeşil ışıkta otomatik başlama
- Şerit tespiti ve takibi
- Engel tespiti ve sollama (turuncu renkli engeller)
- Yaya geçidi ve hemzemin geçitlerde durma
- Kırmızı renkli park alanına park etme

## Donanım Gereksinimleri

- Raspberry Pi 5
- Raspberry Pi Camera 3
- 2 adet DC Motor
- Motor sürücü devresi
- Sarhoş teker (ön)
- Güç kaynağı

## Pin Bağlantıları

- Sol motor: IN1=16, IN2=18, PWM=12
- Sağ motor: IN1=36, IN2=38, PWM=32

## Kurulum

1. Gerekli bağımlılıkları yükleyin:

```bash
pip install -r requirements.txt
```

2. Kamera ve motorların bağlantılarını yapın.

## Kullanım

Ana programı çalıştırmak için:

```bash
python main.py
```

### Test Modları

Trafik ışığı tanıma testini çalıştırmak için:

```bash
python main.py --test-mode traffic_light --debug
```

Motor kontrol testini çalıştırmak için:

```bash
python main.py --test-mode motor
```

### Test Araçları

Test araçları `tests/` klasöründe bulunmaktadır:

```bash
# Trafik ışığı kalibrasyon aracı
python tests/calibrate_traffic_light.py

# Trafik ışığı ve motor testi
python tests/traffic_light_test.py
```

## Modüller

- `traffic_light_detection.py`: Trafik ışığı tanıma modülü
- `motor_control.py`: Motor kontrol modülü
- `main.py`: Ana program
- `tests/traffic_light_test.py`: Trafik ışığı ve motor kontrolü test programı
- `tests/calibrate_traffic_light.py`: Trafik ışığı HSV kalibrasyon aracı

## Konfigürasyon

Trafik ışığı tanıma için HSV renk aralığını ayarlamak için:

```python
detector.set_hsv_range([40, 50, 50], [90, 255, 255])  # Alt ve üst HSV değerleri
```

İlgi alanını (ROI) ayarlamak için:

```python
detector.set_roi(0.25, 0, 0.5, 0.3)  # x, y, genişlik, yükseklik (0-1 arası)
```

## Geliştirme

Bu proje modüler bir yapıda tasarlanmıştır. Yeni özellikler eklemek için ilgili modülleri genişletebilirsiniz.

### Şerit Takibi Ekleme

Şerit takibi için yeni bir modül oluşturun ve `main.py` içindeki `run_autonomous_mode` fonksiyonuna entegre edin.

### Engel Tespiti Ekleme

Engel tespiti için renk filtreleme kullanarak yeni bir modül oluşturun ve ana programa entegre edin.

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. 