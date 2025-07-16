import serial
import time
import re
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal

# ========================
# Parámetros del controlador
# ========================
# Compensador adelanto + atraso + ganancia
Kc = 0.04
z_c = -0.1
p_c = -1.2971
z_a = 0.1
p_a = 0.01

# Planta de segundo orden (usada para diseño)
num_G = [1851051.3]
den_G = [1, 30.65, 892.73]

# Compensador total: (s+z_c)(s+z_a)/(s+p_c)(s+p_a)
num_C = np.polymul([1, -z_c], [1, z_a])
den_C = np.polymul([1, -p_c], [1, p_a])
num_total = Kc * num_C
den_total = den_C

# Discretización del compensador
Ts = 0.1  # Periodo de muestreo en segundos (ajustable)
sys_d = signal.cont2discrete((num_total, den_total), Ts, method='tustin')
b, a = sys_d[0].flatten(), sys_d[1].flatten()

# ========================
# Inicialización de señales
# ========================
u_hist = [0.0, 0.0]  # PWM anteriores
e_hist = [0.0, 0.0]  # errores anteriores

# ========================
# Configuración del puerto
# ========================
puerto = 'COM7'
baudios = 115200
ventana_tiempo = 3.0
duracion_total = 10.0

rpm_ref = float(input("Ingresa la referencia de RPM (ej: 1500): "))

# Listas para graficar
rpm_lista = []
ref_lista = []
tiempos = []
pwm_lista = []
try:
    ser = serial.Serial(puerto, baudios, timeout=0)
    time.sleep(2)
    print("Puerto abierto. Iniciando control...")

    
    plt.ion()
    fig, ax = plt.subplots()
    linea_rpm, = ax.plot([], [], 'b-', label='RPM medida')
    linea_ref, = ax.plot([], [], 'r--', label='RPM referencia')
    ax.set_ylim(-2500, 2500)
    ax.set_xlabel("Tiempo [s]")
    ax.set_ylabel("RPM")
    ax.set_title("Control en tiempo real con compensador (RPM y PWM)")
    ax.grid(True)

    # Segundo eje para PWM
    ax2 = ax.twinx()
    linea_pwm, = ax2.plot([], [], 'g-.', label='PWM (%)')
    ax2.set_ylabel("PWM [%]")
    ax2.set_ylim(-110, 110)

    # Leyendas combinadas
    lines = [linea_rpm, linea_ref, linea_pwm]
    labels = [line.get_label() for line in lines]
    ax.legend(lines, labels, loc='upper right')

    fig.tight_layout()
    t_inicio = time.time()

    while time.time() - t_inicio < duracion_total:
        ser.reset_input_buffer()
        time.sleep(Ts)

        linea = ser.readline().decode(errors='ignore').strip()
        if linea:
            match = re.search(r'RPM:\s*(-?[0-9.]+)', linea)
            if match:
                rpm_actual = float(match.group(1))
                t_actual = time.time() - t_inicio

                # Error de control
                e0 = rpm_ref - rpm_actual

                # Control digital (diferencia de ecuaciones)
                u0 = (
                    b[0]*e0 + b[1]*e_hist[0] + b[2]*e_hist[1]
                    - a[1]*u_hist[0] - a[2]*u_hist[1]
                )

                # Saturación del PWM
                u0 = max(-100, min(100, u0))
                pwm_lista.append(u0)

                # Enviar PWM al motor
                ser.write(f"{int(u0)}\n".encode())

                # Desplazar historial
                e_hist = [e0] + e_hist[:1]
                u_hist = [u0] + u_hist[:1]

                # Guardar y graficar
                tiempos.append(t_actual)
                rpm_lista.append(rpm_actual)
                ref_lista.append(rpm_ref)

                while tiempos and t_actual - tiempos[0] > ventana_tiempo:
                    tiempos.pop(0)
                    rpm_lista.pop(0)
                    ref_lista.pop(0)
                    pwm_lista.pop(0)

                linea_rpm.set_xdata(tiempos)
                linea_rpm.set_ydata(rpm_lista)
                linea_ref.set_xdata(tiempos)
                linea_ref.set_ydata(ref_lista)
                linea_pwm.set_xdata(tiempos)
                linea_pwm.set_ydata(pwm_lista)

                ax.set_xlim(max(0, t_actual - ventana_tiempo), t_actual)
                ax.relim()
                ax.autoscale_view(scaley=True)
                ax2.relim()
                ax2.autoscale_view(scaley=True)

                plt.draw()
                plt.pause(0.001)

except KeyboardInterrupt:
    print("\nControl interrumpido por el usuario.")

except serial.SerialException as e:
    print(f"Error al abrir el puerto: {e}")

finally:
    if 'ser' in locals() and ser.is_open:
        ser.write("0\n".encode())  # Detener motor
        ser.close()
        print("Puerto cerrado.")
    plt.ioff()
    plt.show()
