import numpy as np
import control as ctrl
import matplotlib.pyplot as plt

# Parámetros del compensador continuo
Kc = 9.1946
z_c = 296.8202
p_c = 2737.8931
z_a = 90.1478
p_a = 9.0148
Ts = 0.1  # Tiempo de muestreo

# Crear compensador continuo
num = Kc * np.polymul([1 / z_c, 1], [1 / z_a, 1])
den = np.polymul([1 / p_c, 1], [1 / p_a, 1])
Gc = ctrl.tf(num, den)

# Discretizar con ZOH
Gd = ctrl.c2d(Gc, Ts, method='zoh')

# Crear entrada escalón
n = 50
t = np.arange(n) * Ts
u = np.ones(n)  # Escalón de magnitud 1

# Simular respuesta
t_out, y_out = ctrl.forced_response(Gd, T=t, U=u)

# Graficar
plt.figure()
plt.plot(t_out, y_out, label='Respuesta al escalón')
plt.axhline(0, color='gray', linestyle='--')
plt.xlabel('Tiempo [s]')
plt.ylabel('Salida')
plt.title('Respuesta del compensador discretizado (ZOH)')
plt.grid(True)
plt.legend()
plt.show()
