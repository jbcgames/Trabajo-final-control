import serial
import time
import csv
import matplotlib.pyplot as plt

# Configura tu puerto serial aquí
PORT = 'COM7'  # Cámbialo según sea necesario (Linux: '/dev/ttyUSB0' o '/dev/ttyACM0')
BAUD = 115200
DURATION = 2 # segundos entre cambios de PWM
PWM_VALUES = [40, 100]  # Valores de PWM a enviar
CSV_FILENAME = "datos_motor.csv"

# Conexión al puerto serie
ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)  # Espera a que se estabilice

# Abrir CSV
with open(CSV_FILENAME, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['timestamp', 'angle', 'pwm'])
    absolute_start_time = time.time()
    for pwm in PWM_VALUES:
        # Enviar PWM
        ser.write(f"{pwm}\n".encode())
        print(f"Enviado PWM: {pwm}")
        start_time = time.time()

        # Recolectar datos durante DURATION segundos
        while (time.time() - start_time) < DURATION:
            line = ser.readline().decode().strip()
            try:
                if(time.time() - absolute_start_time >= 0.5):
                    angle = float(line)
                    timestamp = time.time()
                    writer.writerow([timestamp, angle, pwm])
                    print(f"{timestamp:.2f}, ángulo: {angle:.2f}, PWM: {pwm}")
            except ValueError:
                continue  # ignorar líneas vacías o mal formateadas

# Cerrar puerto
ser.close()
print(f"Datos guardados en {CSV_FILENAME}")

# Graficar
import pandas as pd

df = pd.read_csv(CSV_FILENAME)
plt.plot(df['timestamp'] - df['timestamp'][0], df['angle'], label='Ángulo')
plt.plot(df['timestamp'] - df['timestamp'][0], df['pwm'], label='PWM', alpha=0.5)
plt.xlabel('Tiempo (s)')
plt.ylabel('Valor')
plt.legend()
plt.title('Respuesta del motor al cambiar PWM')
plt.grid(True)
plt.show()
