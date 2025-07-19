import serial
import time
import re
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import cont2discrete, place_poles

# ========================
# 1) PARÁMETROS DEL SISTEMA
# ========================
# Matrices de estado continuas (nxn, nx1, 1xn, escalar)
A = np.array([[0, 1],
              [-892.73, -30.65]])
B = np.array([[0],
              [1851051.3]])
C = np.array([[1, 0]])
D = np.array([[0]])

# Tiempo de muestreo
Ts = 0.01  # s

# ------------------------
# Polos deseados (discretos)
# ------------------------
# Define aquí tus polos en z para K y polos para L (más rápidos que K)
poles_K = [0.8 + 0.0j, 0.9 + 0.0j]      # Ejemplo: coloca tus valores
poles_L = [0.5 + 0.0j, 0.6 + 0.0j]      # Observador debe converger rápido

# ========================
# 2) DISCRETIZACIÓN
# ========================
sys_d = cont2discrete((A, B, C, D), Ts, method='tustin')
Ad, Bd, Cd, Dd = sys_d[0], sys_d[1], sys_d[2], sys_d[3]

# ========================
# 3) DISEÑO DE K y L
# ========================
# Realimentación de estados K
Kp = place_poles(Ad, Bd, poles_K)
Kd = Kp.gain_matrix   # matriz 1×n

# Observador de estado L
Lp = place_poles(Ad.T, Cd.T, poles_L)
Ld = Lp.gain_matrix.T  # matriz n×1

# ========================
# 4) GANANCIA DE REFERENCIA Nbar
# ========================
n = Ad.shape[0]
I = np.eye(n)
# Asegura Nbar para seguimiento de escalón sin error en régimen:
Nbar = 1.0 / (Cd @ np.linalg.inv(I - Ad + Bd @ Kd) @ Bd).item()

# ========================
# 5) INICIALIZACIÓN DE HISTORIALES
# ========================
x_hat = np.zeros((n,))  # estimación inicial de estados
u_prev = 0.0            # último control aplicado

# ========================
# 6) CONFIGURACIÓN SERIAL Y GRÁFICOS
# ========================
puerto = 'COM7'
baudios = 115200
duracion_total = 10.0   # segundos de ejecución
rpm_ref = float(input("Ingresa la referencia de RPM (ej: 1500): "))

# Listas para graficar
tiempos = []
rpm_lista = []
ref_lista = []
pwm_lista = []

# Inicializar puerto y gráficos
ser = serial.Serial(puerto, baudios, timeout=0)
time.sleep(2)
plt.ion()
fig, ax = plt.subplots()
linea_rpm, = ax.plot([], [], 'b-', label='RPM medida')
linea_ref, = ax.plot([], [], 'r--', label='RPM referencia')
ax.set_xlabel("Tiempo [s]")
ax.set_ylabel("RPM")
ax.grid(True)

ax2 = ax.twinx()
linea_pwm, = ax2.plot([], [], 'g-.', label='PWM (%)')
ax2.set_ylabel("PWM [%]")

lines = [linea_rpm, linea_ref, linea_pwm]
labels = [l.get_label() for l in lines]
ax.legend(lines, labels, loc='upper right')
fig.tight_layout()

# ========================
# 7) BUCLE DE CONTROL
# ========================
t0 = time.time()
try:
    while time.time() - t0 < duracion_total:
        t_act = time.time() - t0
        ser.reset_input_buffer()
        time.sleep(Ts)

        linea = ser.readline().decode(errors='ignore').strip()
        if not linea:
            continue

        m = re.search(r'RPM:\s*(-?[0-9.]+)', linea)
        if not m:
            continue

        y = float(m.group(1))  # medición de RPM

        # — Estimador (observador de estados) —
        x_hat = Ad @ x_hat + Bd.flatten()*u_prev + Ld.flatten()*(y - Cd @ x_hat)

        # — Ley de control por realimentación de estados —
        # u = -K x̂ + Nbar * r
        u = float(-Kd @ x_hat + Nbar * rpm_ref)
        u = max(-100, min(100, u))  # saturación PWM

        # Envío de PWM
        ser.write(f"{int(u)}\n".encode())
        u_prev = u

        # Guardar datos para gráfica
        tiempos.append(t_act)
        rpm_lista.append(y)
        ref_lista.append(rpm_ref)
        pwm_lista.append(u)

        # Actualizar gráfico
        linea_rpm.set_data(tiempos, rpm_lista)
        linea_ref.set_data(tiempos, ref_lista)
        linea_pwm.set_data(tiempos, pwm_lista)

        ax.set_xlim(0, max(1, t_act))
        ax.set_ylim(min(rpm_lista + [rpm_ref]) - 100, max(rpm_lista + [rpm_ref]) + 100)
        ax2.set_ylim(min(pwm_lista) - 10, max(pwm_lista) + 10)

        plt.draw()
        plt.pause(0.001)

except KeyboardInterrupt:
    print("\nControl interrumpido por el usuario.")

finally:
    # Apagar motor y cerrar puerto
    ser.write("0\n".encode())
    ser.close()
    plt.ioff()
    plt.show()
