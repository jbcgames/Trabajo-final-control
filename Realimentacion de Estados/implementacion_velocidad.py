
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

# --- Referencia inicial de velocidad (RPM) ---
velocidad_ref = 0.0
ser.write(f"{int(velocidad_ref)}\n".encode())

# --- Función para cambiar velocidad por consola ---
def leer_consola():
    global velocidad_ref
    while True:
        try:
            entrada = input("Nueva velocidad deseada (RPM): ")
            nuevo = float(entrada.strip())
            if 0 <= nuevo <= 2500:
                velocidad_ref = nuevo
                ser.write(f"{int(velocidad_ref)}\n".encode())
                print(f"[PC] Nueva referencia: {velocidad_ref:.1f} RPM")
            else:
                print("[PC] Valor fuera de rango.")
        except:
            print("[PC] Entrada inválida.")

# --- Lanzar hilo para entrada por consola ---
hilo_consola = threading.Thread(target=leer_consola, daemon=True)
hilo_consola.start()

# --- Configurar gráfica en tiempo real ---
plt.ion()
fig, ax = plt.subplots()
line_ref, = ax.plot([], [], 'r--', label='Velocidad deseada')
line_rpm, = ax.plot([], [], 'b-', label='Velocidad actual')
line_pwm, = ax.plot([], [], 'g-', label='PWM aplicado')
ax.set_title("Seguimiento de velocidad en tiempo real")
ax.set_xlabel("Tiempo (s)")
ax.set_ylabel("Valor")
ax.grid(True)
ax.legend(loc="upper right")

buffer_size = 300
tiempo = deque(maxlen=buffer_size)
rpm_real = deque(maxlen=buffer_size)
pwm_aplicado = deque(maxlen=buffer_size)
rpm_deseada = deque(maxlen=buffer_size)

t_inicial = time.time()

# --- Bucle principal ---
while True:
    try:
        ser.reset_input_buffer()
        linea = ser.readline().decode().strip()
        match = re.search(r"RPM:\s*([-+]?[0-9]*\.?[0-9]+)\s*,\s*PWM:\s*([-+]?[0-9]*\.?[0-9]+)", linea)
        if match:
            rpm = float(match.group(1))
            pwm = float(match.group(2))

            t_actual = time.time() - t_inicial
            tiempo.append(t_actual)
            rpm_real.append(rpm)
            pwm_aplicado.append(pwm)
            rpm_deseada.append(velocidad_ref)

            line_ref.set_data(tiempo, rpm_deseada)
            line_rpm.set_data(tiempo, rpm_real)
            line_pwm.set_data(tiempo, pwm_aplicado)
            ax.set_xlim(max(0, t_actual - 10), t_actual + 1)
            ax.set_ylim(0, 2200)
            fig.canvas.draw()
            fig.canvas.flush_events()

            print(f"[PC] Ref: {velocidad_ref:.1f} RPM, Actual: {rpm:.2f} RPM, PWM: {pwm:.2f}%")

        time.sleep(0.01)

    except KeyboardInterrupt:
        print("Interrumpido por el usuario.")
        break
