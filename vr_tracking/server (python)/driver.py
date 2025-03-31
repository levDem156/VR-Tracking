import pigpio
import time
import math
import json

# === Калибровка параметров для MG996R ===
# Эти значения могут быть откалиброваны экспериментально.
MIN_PULSE = 500     # минимальная длительность импульса в мкс (примерно соответствует 0°)
MAX_PULSE = 2500    # максимальная длительность импульса в мкс (примерно соответствует 180°)
# При необходимости можно откорректировать эти значения,
# чтобы сервопривод не "ударялась" об концевые положения.

# === Параметры сглаживания ===
ALPHA = 0.2              # коэффициент экспоненциального сглаживания (0 < ALPHA < 1)
UPDATE_INTERVAL = 0.05   # интервал обновления (в секундах)

# === Номера пинов (используем нумерацию BCM, т.к. pigpio работает с ними) ===
# Исходя из вашего BOARD-распиновки:
# BOARD 32 -> BCM 12, BOARD 12 -> BCM 18, BOARD 33 -> BCM 13
YAW_PIN   = 12   # сервопривод для yaw (угол поворота)
PITCH_PIN = 18   # сервопривод для pitch (наклон)
ROLL_PIN  = 13   # сервопривод для roll (крен), при необходимости сигнал инвертируется

# === Функции для преобразования углов и вычисления импульса ===

def normalize_angle(angle):
    """
    Нормализация угла в радианах в диапазоне [-π, π].
    """
    angle = angle % (2 * math.pi)
    if angle > math.pi:
        angle -= 2 * math.pi
    return angle

def init_servo_angle(angle_rad, invert=False):
    """
    Преобразует угол, заданный в радианах, в значение в градусах от 0 до 180,
    применяя нормализацию и ограничение диапазона (-90°..+90°) с последующим смещением.
    Если параметр invert=True, меняет знак угла (для инверсии направления).
    """
    if invert:
        angle_rad = -angle_rad
    angle_rad = normalize_angle(angle_rad)
    angle_deg = math.degrees(angle_rad)
    # Ограничиваем угол диапазоном [-90, +90]
    if angle_deg > 90:
        angle_deg = 90
    elif angle_deg < -90:
        angle_deg = -90
    # Смещаем в диапазон 0-180
    return angle_deg + 90

def angle_to_pulse(angle_deg):
    """
    Преобразует угол (0-180 градусов) в длительность импульса в микросекундах.
    Используется линейная интерполяция между MIN_PULSE и MAX_PULSE.
    """
    pulse = MIN_PULSE + (angle_deg / 180.0) * (MAX_PULSE - MIN_PULSE)
    return int(pulse)

def read_orientation(file_path="orientation.json"):
    """
    Читает JSON-файл с ориентацией. Ожидается, что в файле содержатся ключи "y", "p" и "r"
    (углы в радианах для yaw, pitch и roll соответственно).
    Если файл отсутствует или имеет ошибки, возвращается None.
    """
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        return data.get("y", 0.0), data.get("p", 0.0), data.get("r", 0.0)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def main():
    # === Инициализация pigpio ===
    pi = pigpio.pi()
    if not pi.connected:
        print("Ошибка: Не удалось подключиться к pigpio демону. Запустите 'sudo pigpiod'")
        return

    # === Первоначальная установка углов сервоприводов ===
    # При наличии корректного файла orientation.json, устанавливаем стартовые значения,
    # иначе – центр (90°)
    orientation = read_orientation()
    if orientation:
        yaw_rad, pitch_rad, roll_rad = orientation
        servo_yaw_angle   = init_servo_angle(yaw_rad)
        servo_pitch_angle = init_servo_angle(pitch_rad)
        servo_roll_angle  = init_servo_angle(roll_rad, invert=True)
    else:
        servo_yaw_angle = servo_pitch_angle = servo_roll_angle = 90

    # Устанавливаем начальные импульсы
    pi.set_servo_pulsewidth(YAW_PIN, angle_to_pulse(servo_yaw_angle))
    pi.set_servo_pulsewidth(PITCH_PIN, angle_to_pulse(servo_pitch_angle))
    pi.set_servo_pulsewidth(ROLL_PIN, angle_to_pulse(servo_roll_angle))

    print("Запуск цикла управления. Для остановки нажмите Ctrl+C.")
    try:
        while True:
            orientation = read_orientation()
            if orientation is None:
                time.sleep(UPDATE_INTERVAL)
                continue
            
            
            yaw_rad, pitch_rad, roll_rad = orientation
            
            # Вычисляем целевые углы в градусах (0-180)
            target_yaw   = init_servo_angle(yaw_rad)
            target_pitch = init_servo_angle(pitch_rad)
            target_roll  = init_servo_angle(roll_rad, invert=True)

            # Применяем экспоненциальное сглаживание для плавного перехода
            servo_yaw_angle   = servo_yaw_angle   + ALPHA * (target_yaw   - servo_yaw_angle)
            servo_pitch_angle = servo_pitch_angle + ALPHA * (target_pitch - servo_pitch_angle)
            servo_roll_angle  = servo_roll_angle  + ALPHA * (target_roll  - servo_roll_angle)

            # Преобразуем сглажённый угол в длительность импульса (мкс)
            pulse_yaw   = angle_to_pulse(servo_yaw_angle)
            pulse_pitch = angle_to_pulse(servo_pitch_angle)
            pulse_roll  = angle_to_pulse(servo_roll_angle)

            # Обновляем PWM для каждого канала
            pi.set_servo_pulsewidth(YAW_PIN, pulse_yaw)
            pi.set_servo_pulsewidth(PITCH_PIN, pulse_pitch)
            pi.set_servo_pulsewidth(ROLL_PIN, pulse_roll)

            time.sleep(UPDATE_INTERVAL)
    except KeyboardInterrupt:
        print("\nПрограмма остановлена пользователем.")
    finally:
        # Отключаем сервоприводы (передаём 0 мкс)
        pi.set_servo_pulsewidth(YAW_PIN, 0)
        pi.set_servo_pulsewidth(PITCH_PIN, 0)
        pi.set_servo_pulsewidth(ROLL_PIN, 0)
        pi.stop()

if __name__ == '__main__':
    main()