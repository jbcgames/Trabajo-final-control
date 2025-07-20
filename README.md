
#  Control de Velocidad y Posición en Motor DC

Este proyecto implementa el control avanzado de un motor de corriente continua utilizando dos enfoques distintos: un **compensador adelanto–atraso** y un **controlador por realimentación de estados**. Todo el desarrollo se basa en simulación, identificación experimental e implementación embebida en tiempo real.

---

##  Objetivo

Diseñar, simular y validar dos estrategias de control para un motor DC, integrando teoría de control moderno con pruebas reales en hardware. El sistema final permite controlar tanto la **velocidad** como la **posición** del motor.

---

##  Tecnologías y Herramientas

- Python (control, numpy, matplotlib)
- MicroPython sobre ESP32C3
- Sensor AS5600 (posición)
- Driver L298N (control PWM)
- Jupyter Notebooks
- PowerPoint para presentación
- GitHub para versionamiento

---

##  Modelado del Sistema

Se identificó experimentalmente la planta, obteniendo:

- Ganancia: `K = 2047.05`
- Frecuencia natural: `wn = 11.42 rad/s`
- Amortiguamiento: `zeta = 0.572`

Función de transferencia:

```
G(s) = 2.671e5 / (s^2 + 13.07s + 130.5)
```

---

##  Controladores Implementados

### 1. Compensador Adelanto–Atraso
- Diseñado en el dominio de la frecuencia para mejorar margen de fase.
- Implementado desde PC con control serial.
- Logra baja oscilación y buen tiempo de respuesta.

### 2. Realimentación de Estados (Velocidad)
- Modelo en espacio de estados con dos variables.
- Ganancia: `K = [0.042, 0.0028]`
- Precompensación: `N_bar = 0.0139`
- Ejecutado en tiempo real en el microcontrolador.

### 3. Realimentación de Estados (Posición)
- Modelo extendido con posición integrada y aceleración.
- Ganancia: `K = [0.35, 0.045, 0.0015]`
- Precompensación: `N_bar = 0.0151`
- Control suave, sin oscilaciones, ideal para seguimiento.

---

##  Resultados

- Excelente seguimiento de referencia.
- Respuestas rápidas con bajo sobreimpulso.
- Buen rechazo a perturbaciones.
- Controladores implementados 100 % en tiempo real.

---

##  Estructura del Repositorio

```
├── Adelanto Atraso/
│   ├── Diseño de compensador adelanto - atraso.ipynb
│   └── implementacion.py
├── Lectura Motor/
│   ├── decodificador_rpm.py
│   ├── leer Controlador.py
│   └── Microcontrolador.py
├── Realimentacion de Estados/
│   ├── EspaciosEstadosPosicionVelocidad.ipynb
│   ├── Implementacion_Posicion_micro.py
│   ├── Implementacion_Posicion.py
│   ├── Implementacion_Velocidad_micro.py
|   └── Implementacion_Velocidad.py
├── Control Velocidad Motor DC.ipynb
├── Link_Video.txt
└── README.md
```

---

##  Video Pitch

Incluye presentación de resultados, diseño de controladores y demostraciones prácticas del sistema en funcionamiento. *https://youtu.be/MQJUslfhQaE*

---

##  Autores

**Miguel Angel Alvarez Guzman**
**Andres David Guerrero Rivera**
**Jose Vicente Zabaleta Montiel**

Proyecto Final de Control Continuo - 2025

---
