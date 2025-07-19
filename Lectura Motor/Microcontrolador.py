from machine import Pin, PWM, I2C
from as5600 import AS5600
import time
import sys
import select

# PWM setup
pwmA = PWM(Pin(2))
pwmB = PWM(Pin(3))
pwmA.freq(1000)
pwmB.freq(1000)

# I2C para AS5600
i2c = I2C(0, scl=Pin(1), sda=Pin(0))
sensor = AS5600(i2c)

# PWM inicial
pwm_value = 0

# Ángulo inicial como referencia
angle_offset = sensor.read_angle_deg()
print(f"Ángulo de referencia: {angle_offset:.2f}°")

# Variables para RPM
prev_angle = sensor.read_angle_deg()
prev_time = time.ticks_us()
rpm = 0

# Contador para imprimir con menos frecuencia
print_counter = 0

def motor_pwm(percent):
    duty = int(abs(percent) * 65535 / 100)
    if percent > 0:
        pwmA.duty_u16(duty)
        pwmB.duty_u16(0)
    elif percent < 0:
        pwmA.duty_u16(0)
        pwmB.duty_u16(duty)
    else:
        pwmA.duty_u16(0)
        pwmB.duty_u16(0)

# Bucle principal
while True:
    # Leer comando PWM del terminal si hay entrada
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        try:
            line = sys.stdin.readline().strip()
            pwm_value = int(line)
            motor_pwm(pwm_value)
        except:
            pass

    # Tiempo actual en microsegundos
    current_time = time.ticks_us()
    dt = time.ticks_diff(current_time, prev_time) / 1_000_000  # a segundos

    if dt >= 0.002:  # mínimo 2 ms
        angle = sensor.read_angle_deg()
        angle_rel = (angle - angle_offset) % 360

        delta_angle = (angle - prev_angle) % 360
        if delta_angle > 180:
            delta_angle -= 360  # corrección si giró en sentido contrario

        rpm = (delta_angle / 360) / dt * 60

        prev_angle = angle
        prev_time = current_time

        print_counter += 1
        if print_counter >= 20:  # imprime cada 20 actualizaciones (~40 ms)
            print(f"Ángulo: {angle_rel:.2f}°, RPM: {rpm:.2f}")
            print_counter = 0

    # Muy pequeño para evitar saturación de CPU
    time.sleep_us(300)
