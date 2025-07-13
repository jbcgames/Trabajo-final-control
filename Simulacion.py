import serial
import time
import matplotlib.pyplot as plt

# === Parámetros ===
PORT = 'COM7'
BAUD = 115200
UPDATE_INTERVAL = 0.1  # segundos entre actualizaciones

# Ganancias del controlador por estados
rpm_ref = 1500
k1 = -0.000369976529 
k2 = -0.00000836456295 
Nbar = 0.00010964213

# Conexión serial
ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)
print("Conectado")

# Enviar parámetros
comando = f"{rpm_ref} {k1} {k2} {Nbar}\n"
ser.write(comando.encode())
print(f"Enviado: {comando.strip()}")

# Configurar gráfica
plt.ion()
fig, ax = plt.subplots()
line_rpm, = ax.plot([], [], label="RPM")
ax.set_xlabel("Tiempo (s)")
ax.set_ylabel("RPM")
ax.set_title("RPM con realimentación de estados")
ax.grid(True)
ax.legend()

tiempos = []
rpms = []
last_update = time.time()

try:
    while True:
        line = ser.readline().decode().strip()
        try:
            if line:
                partes = line.split(",")
                if len(partes) == 3:
                    t = float(partes[0])
                    rpm = float(partes[1].split(":")[1])
                    pos = float(partes[2].split(":")[1])

                    print(f"{t:.3f}s | RPM = {rpm:.2f} | Pos = {pos:.2f}°")

                    if time.time() - last_update >= UPDATE_INTERVAL:
                        tiempos.append(t)
                        rpms.append(rpm)
                        line_rpm.set_data(tiempos, rpms)
                        ax.set_xlim(max(0, t - 5), t + 0.1)
                        ax.set_ylim(min(rpms[-200:]) - 10, max(rpms[-200:]) + 10)
                        fig.canvas.draw()
                        fig.canvas.flush_events()
                        last_update = time.time()
        except Exception as e:
            print("Error:", e)
except KeyboardInterrupt:
    print("Terminando...")
finally:
    ser.close()
    plt.ioff()
    plt.show()
