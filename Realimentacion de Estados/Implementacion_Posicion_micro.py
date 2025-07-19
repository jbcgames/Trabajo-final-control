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
posicion_ref = 0.0  # ángulo deseado
prev_angle = sensor.read_angle_deg()
prev_time = time.ticks_us()
prev_vel = 0
pwm_actual = 0
rpm = 0
angulo = 0
posicion = 0  # posición integrada
velocidad = 0

# --- Ganancia de realimentación de estados y precompensación ---
# Supongamos: K_pos = [k0, k1, k2] y N_bar_pos = 0.0151 (ajustar con valores reales)
K_pos = [0.35, 0.045, 0.0015]   # ejemplo: [posición, velocidad, aceleración]
N_bar_pos = 0.0151

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
    # Leer ángulo de referencia desde serial si disponible
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        try:
            linea = sys.stdin.readline().strip()
            posicion_ref = float(linea)
        except:
            pass

    # Calcular tiempo
    current_time = time.ticks_us()
    dt = time.ticks_diff(current_time, prev_time) / 1_000_000  # segundos

    if dt >= 0.005:
        angulo = sensor.read_angle_deg()

        # velocidad
        delta_angle = (angulo - prev_angle) % 360
        if delta_angle > 180:
            delta_angle -= 360
        velocidad = (delta_angle / 360) / dt * 60  # RPM

        # posición = integración de velocidad
        posicion += velocidad * dt  # RPM * s ~ unidad relativa

        # aceleración estimada (derivada de velocidad)
        aceleracion = (velocidad - prev_vel) / dt

        # Estados
        x = [posicion, velocidad, aceleracion]
        r = posicion_ref

        # Control: u = -Kx + N_bar * r
        u = -(K_pos[0]*x[0] + K_pos[1]*x[1] + K_pos[2]*x[2]) + N_bar_pos * r

        # Saturación
        u = max(min(u, 100), -100)

        # Zona muerta
        if abs(u) < PWM_MIN and abs(u) > 0:
            u = PWM_MIN if u > 0 else -PWM_MIN

        # Si está dentro del 10% de la posición deseada, no aplicar control
        if abs(posicion - posicion_ref) < 0.10 * abs(posicion_ref):
            u = 0

        motor_pwm(u)
        pwm_actual = u

        prev_time = current_time
        prev_angle = angulo
        prev_vel = velocidad

        # Imprimir cada 40 ms
        print_counter += 1
        if print_counter >= 8:
            print(f"Pos: {posicion:.2f}, Vel: {velocidad:.2f}, PWM: {pwm_actual:.2f}")
            print_counter = 0