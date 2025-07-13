import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Cargar CSV
archivo = 'C:\Users\USER\OneDrive\Documentos\mediciones_rpm.csv'  # Cambia esto si el archivo tiene otro nombre
datos = pd.read_csv(archivo)

# Extraer columnas
tiempo = datos['tiempo'].values
rpm = datos['rpm'].values
pwm = datos['pwm'].values

# Paso 1: Normalizar la respuesta (RPM) con respecto al cambio de entrada PWM
delta_pwm = pwm[-1] - pwm[0]
delta_rpm = rpm - rpm[0]  # Quitar el offset inicial

# Respuesta normalizada (idealmente entre 0 y 1)
respuesta_norm = delta_rpm / (rpm[-1] - rpm[0])

# Paso 2: Encontrar el tiempo en que la respuesta alcanza el 63.2%
valor_632 = 0.632
indice_tau = np.argmin(np.abs(respuesta_norm - valor_632))
tau_aprox = tiempo[indice_tau] - tiempo[0]

# Paso 3: Ganancia estática
ganancia_K = (rpm[-1] - rpm[0]) / delta_pwm if delta_pwm != 0 else 0

# Mostrar resultados
print(f"Ganancia (K): {ganancia_K:.4f}")
print(f"Constante de tiempo (tau): {tau_aprox:.4f} segundos")

# Graficar
plt.figure(figsize=(10, 5))
plt.plot(tiempo, rpm, label='RPM')
plt.axhline(y=rpm[0] + 0.632 * (rpm[-1] - rpm[0]), color='r', linestyle='--', label='63.2% de respuesta')
plt.axvline(x=tiempo[indice_tau], color='g', linestyle='--', label='τ estimado')
plt.title('Estimación de parámetros de sistema de primer orden')
plt.xlabel('Tiempo [s]')
plt.ylabel('RPM')
plt.legend()
plt.grid(True)
plt.show()
