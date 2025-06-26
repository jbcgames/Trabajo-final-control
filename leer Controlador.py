import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import time

# Configura tu puerto y velocidad
PORT = 'COM6'     # Cámbialo a '/dev/ttyUSB0' o similar en Linux
BAUDRATE = 115200
BUFFER_SIZE = 200

# Inicializar buffers
angulo_buffer = deque([0.0]*BUFFER_SIZE, maxlen=BUFFER_SIZE)
rpm_buffer = deque([0.0]*BUFFER_SIZE, maxlen=BUFFER_SIZE)

# Inicializar conexión serial
ser = serial.Serial(PORT, BAUDRATE, timeout=1)

# Variables para cálculo de RPM
ultimo_angulo = None
ultimo_tiempo = None

def corregir_delta_angulo(delta):
    if delta > 180:
        delta -= 360
    elif delta < -180:
        delta += 360
    return delta

def update(frame):
    global ultimo_angulo, ultimo_tiempo

    try:
        line = ser.readline().decode().strip()
        if line:
            angulo = float(line)
            angulo_buffer.append(angulo)

            t_actual = time.time()

            if ultimo_angulo is not None and ultimo_tiempo is not None:
                delta_angulo = corregir_delta_angulo(angulo - ultimo_angulo)
                delta_tiempo = t_actual - ultimo_tiempo

                if delta_tiempo > 0:
                    rpm = (delta_angulo / 360.0) / delta_tiempo * 60.0
                    rpm_buffer.append(rpm)
                else:
                    rpm_buffer.append(0.0)
            else:
                rpm_buffer.append(0.0)

            ultimo_angulo = angulo
            ultimo_tiempo = t_actual

    except Exception as e:
        print("Error:", e)

    # Graficar ángulo
    ax1.clear()
    ax1.plot(angulo_buffer)
    ax1.set_ylim(0, 360)
    ax1.set_title("Ángulo AS5600 (grados)")
    ax1.set_ylabel("Ángulo (°)")
    ax1.set_xlabel("Muestras")

    # Graficar RPM
    ax2.clear()
    ax2.plot(rpm_buffer, color='orange')
    ax2.set_ylim(0, max(100, max(rpm_buffer)))
    ax2.set_title("Velocidad angular (RPM)")
    ax2.set_ylabel("RPM")
    ax2.set_xlabel("Muestras")

# Crear figura y ejes
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))
ani = animation.FuncAnimation(fig, update, interval=1)
plt.tight_layout()
plt.show()
