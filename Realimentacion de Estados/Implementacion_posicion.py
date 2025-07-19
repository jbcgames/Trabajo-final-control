
import serial
import time
import re
import threading
import matplotlib.pyplot as plt
from collections import deque

# --- Configuración del puerto serial ---
puerto = 'COM7'  # Cambia según tu sistema
baudrate = 115200
ser = serial.Serial(puerto, baudrate, timeout=1)
time.sleep(2)

# --- Referencia inicial (global) ---
angulo_ref = 180.0
ser.write(f"{int(angulo_ref)}\n".encode())

# --- Función para escuchar entrada del usuario ---
def leer_consola():
    global angulo_ref
    while True:
        try:
            entrada = input("Nuevo ángulo deseado (0–360): ")
            nuevo = float(entrada.strip())
            if 0 <= nuevo <= 360:
                angulo_ref = nuevo
                ser.write(f"{int(angulo_ref)}\n".encode())
                print(f"[PC] Se actualizó la referencia a {angulo_ref:.1f}°")
            else:
                print("[PC] Valor fuera de rango.")
        except:
            print("[PC] Entrada inválida.")

# --- Lanzar hilo para entrada de consola ---
hilo_consola = threading.Thread(target=leer_consola, daemon=True)
hilo_consola.start()

# --- Configuración de gráfica en tiempo real ---
plt.ion()
fig, ax = plt.subplots()
line_ref, = ax.plot([], [], 'r--', label='Ángulo deseado')
line_ang, = ax.plot([], [], 'b-', label='Ángulo actual')
line_pwm, = ax.plot([], [], 'g-', label='PWM aplicado')
ax.set_title("Seguimiento del ángulo y PWM en tiempo real")
ax.set_xlabel("Tiempo (s)")
ax.set_ylabel("Valor")
ax.grid(True)
ax.legend(loc="upper right")

buffer_size = 300
tiempo = deque(maxlen=buffer_size)
angulo_real = deque(maxlen=buffer_size)
pwm_aplicado = deque(maxlen=buffer_size)
angulo_deseado = deque(maxlen=buffer_size)

t_inicial = time.time()

# --- Bucle principal de graficación ---
while True:
    try: 
        ser.reset_input_buffer()
        linea = ser.readline().decode().strip()
        match = re.search(r"Ángulo:\s*([-+]?[0-9]*\.?[0-9]+)°\s*,\s*RPM:\s*([-+]?[0-9]*\.?[0-9]+)\s*,\s*PWM:\s*([-+]?[0-9]*\.?[0-9]+)", linea)
        if match:
            angulo = float(match.group(1))
            pwm = float(match.group(3))

            t_actual = time.time() - t_inicial
            tiempo.append(t_actual)
            angulo_real.append(angulo)
            pwm_aplicado.append(pwm)
            angulo_deseado.append(angulo_ref)

            line_ref.set_data(tiempo, angulo_deseado)
            line_ang.set_data(tiempo, angulo_real)
            line_pwm.set_data(tiempo, pwm_aplicado)
            ax.set_xlim(max(0, t_actual - 10), t_actual + 1)
            ax.set_ylim(-50, 360)
            fig.canvas.draw()
            fig.canvas.flush_events()

            print(f"[PC] Ref: {angulo_ref:.1f}°, Ang: {angulo:.2f}°, PWM: {pwm:.2f}%")

        time.sleep(0.001)

    except KeyboardInterrupt:
        print("Interrumpido por el usuario.")
        break
