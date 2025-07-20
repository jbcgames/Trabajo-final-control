
#  Control de Velocidad y Posición en Motor DC

Este proyecto implementa el control avanzado de un motor de corriente continua utilizando dos enfoques distintos: un **compensador adelanto–atraso** y un **controlador por realimentación de estados**. Todo el desarrollo se basa en simulación, identificación experimental e implementación embebida en tiempo real.

---

##  Objetivo

Diseñar, simular y validar dos estrategias de control para un motor DC, integrando teoría de control moderno con pruebas reales en hardware. El sistema final permite controlar tanto la **velocidad** como la **posición** del motor.

---

##  Tecnologías y Herramientas

- Python (control, numpy, matplotlib)
- MicroPython sobre RP2040 (Pico)
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
├── notebooks/
│   ├── Diseño de compensador adelanto - atraso.ipynb
│   └── EspaciosEstadosPosicionVelocidad.ipynb
├── micro/
│   ├── micro_control_velocidad.py
│   ├── micro_control_estados_velocidad.py
│   └── micro_control_estados_posicion.py
├── pc/
│   ├── pc_control_velocidad_grafica.py
│   ├── pc_grafica_interactiva.py
│   └── pc_grafica_angulo_pwm.py
├── Presentacion_Control_Motor_DC.pptx
└── README.md
```

---

##  Video Pitch

Incluye presentación de resultados, diseño de controladores y demostraciones prácticas del sistema en funcionamiento. *(link aquí cuando esté publicado)*

---

##  Autores

**Miguel Angel Alvarez Guzman**
**Andres David Guerrero Rivera**
**Jose Vicente Zabaleta Montiel**

Proyecto Final de Control Moderno - 2025

---
