# Generar código completo en MicroPython para control por estados con precompensación en velocidad

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

# Variables
velocidad_ref = 0.0  # RPM deseada
prev_angle = sensor.read_angle_deg()
prev_time = time.ticks_us()
pwm_actual = 0
rpm = 0

# --- Control por realimentación de estados ---
# Supongamos que K fue calculado en Python como: [0.042, 0.0028]
# Y N_bar = 0.0139 (para seguimiento exacto de referencia)
K1 = 0.042
N_bar = 0.00012572

# PWM mínimo efectivo
PWM_MIN = 27

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
print_counter = 0
while True:
    # Leer velocidad de referencia desde serial si disponible
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        try:
            linea = sys.stdin.readline().strip()
            velocidad_ref = float(linea)
        except:
            pass

    # Calcular tiempo
    current_time = time.ticks_us()
    dt = time.ticks_diff(current_time, prev_time) / 1_000_000  # segundos

    if dt >= 0.005:  # al menos 5 ms
        angle = sensor.read_angle_deg()

        delta_angle = (angle - prev_angle) % 360
        if delta_angle > 180:
            delta_angle -= 360

        rpm = (delta_angle / 360) / dt * 60

        # Estado: solo usamos x1 = rpm
        x1 = rpm
        reference = velocidad_ref

        # Control con precompensación
        u = -K1 * x1 + N_bar * reference

        # Saturación
        u = max(min(u, 100), -100)

        # Zona muerta
        if abs(u) < PWM_MIN and abs(u) > 0:
            u = PWM_MIN if u > 0 else -PWM_MIN

        # Si dentro del 10% del valor deseado, no aplicar control
        if abs(reference - rpm) < 0.10 * abs(reference):
            u = 0

        motor_pwm(u)
        pwm_actual = u

        prev_angle = angle
        prev_time = current_time

        # Imprimir cada 40 ms aprox.
        print_counter += 1
        if print_counter >= 8:
            print(f"RPM: {rpm:.2f}, PWM: {pwm_actual:.2f}")
            print_counter = 0
