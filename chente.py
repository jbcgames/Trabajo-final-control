import random

# Generar número aleatorio entre 1 y 10
numero_secreto = random.randint(1, 10)

# Pedir al usuario que adivine
intento = int(input("Adivina el número (entre 1 y 10): "))

# Verificar si adivinó
if intento == numero_secreto:
    print("¡Correcto! Adivinaste el número.")
else:
    print(f"Lo siento, el número era {numero_secreto}. ¡Sigue intentando!")
