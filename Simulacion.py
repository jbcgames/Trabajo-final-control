import serial
import time
import matplotlib.pyplot as plt
import numpy as np
from collections import deque

# === CONFIGURACIÓN ===
PORT = 'COM7'
BAUD = 115200
Ts = 0.01  # período de muestreo
DURATION = 100  # duración total en segundos

# Controlador discretizado
b0 = 0.02754545
b1 = -0.027
a1 = -0.81818182

referencia = 1000.0  # RPM deseada
umbral_pwm = 30      # mínimo PWM para romper fricción

# Variables del controlador
e = 0
e_prev = 0
u = 0
u_prev = 0

angulo_prev = None
t_prev = None

# Comunicación Serial
ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)

# === Preparar gráfica en tiempo real ===
plt.ion()
fig, ax = plt.subplots()
ax.set_ylim(0, 1200)
ax.set_xlim(0, DURATION)
ax.set_xlabel("Tiempo (s)")
ax.set_ylabel("RPM")
ax.set_title("Velocidad del motor en tiempo real")

line_rpm, = ax.plot([], [], label='RPM')
line_ref, = ax.plot([], [], 'r--', label='Referencia')
ax.legend()

# Buffers de datos para la gráfica
t_buffer = deque(maxlen=500)
rpm_buffer = deque(maxlen=500)

# Tiempo base
start_time = time.time()
absolute_start_time = start_time

# === Bucle de control ===
while (time.time() - start_time) < DURATION:
    line = ser.readline().decode().strip()
    try:
        if line == '':
            continue
        angle = float(line)
        timestamp = time.time()

        if timestamp - absolute_start_time < 0.5:
            angulo_prev = angle
            t_prev = timestamp
            continue

        # Calcular RPM
        dt = timestamp - t_prev
        delta = (angle - angulo_prev) % 360
        if delta > 180:
            delta -= 360
        rpm_actual = (delta / dt) * (60 / 360)

        # Controlador discreto
        e = referencia - rpm_actual
        u = b0 * e + b1 * e_prev - a1 * u_prev
        pwm = max(min(u, 100), -100)

        # Aplicar umbral mínimo para evitar atascos
        if abs(rpm_actual) < 20 and abs(pwm) < umbral_pwm:
            pwm = umbral_pwm if pwm >= 0 else -umbral_pwm

        # Enviar al ESP32
        ser.write(f"{int(pwm)}\n".encode())

        # Actualizar estados
        e_prev = e
        u_prev = u
        angulo_prev = angle
        t_prev = timestamp

        # Agregar datos al buffer
        t_buffer.append(timestamp - absolute_start_time)
        rpm_buffer.append(rpm_actual)

        # Actualizar gráfica
        line_rpm.set_data(t_buffer, rpm_buffer)
        line_ref.set_data(t_buffer, [referencia] * len(t_buffer))
        ax.set_xlim(max(0, t_buffer[0]), max(2, t_buffer[-1]))
        ax.figure.canvas.draw()
        ax.figure.canvas.flush_events()

        # Esperar siguiente iteración
        time.sleep(Ts)

    except ValueError:
        continue

ser.close()
print("Control finalizado.")
