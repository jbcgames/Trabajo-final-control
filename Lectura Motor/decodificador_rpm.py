import pandas as pd
import matplotlib.pyplot as plt

CSV_FILENAME = "datos_motor.csv"
df = pd.read_csv(CSV_FILENAME)

# Ordenar por tiempo por si acaso
df = df.sort_values('timestamp').reset_index(drop=True)

time=[]
rpm=[]
# Calculo RPM
a=0
# Verificar si los datos son ascendentes o descendentes

try:
    for i in range(len(df['angle'])):
        angulo_actual = int(df['angle'][i])
        angulo_siguiente = int(df['angle'][i+1])
        if(int(df['angle'][i]) == int(df['angle'][i+1])):
            print("No hay cambio de ángulo")
            time.append(df['timestamp'][i]-df['timestamp'][0]) # Si no hay cambio de ángulo, se toma el tiempo actual
            rpm.append(0)
            a+=1
        elif(df['angle'][i+1]> df['angle'][i]):# Si el ángulo disminuye, significa que ha dado una vuelta completa
            time.append(df['timestamp'][i]-df['timestamp'][0])
            rpm.append(60/(time[a]-time[a-1])) # Calculo de RPM
            if rpm[a] > 8000:
                rpm[a] = rpm[a-1] # Si la RPM es mayor a 8000, se toma el valor anterior
            a+=1

except:
    print(len(time))
# Graficar
plt.plot(time, rpm, label='RPM')
plt.xlabel('Tiempo (s)')
plt.ylabel('RPM')
plt.title('RPM del motor')
plt.grid(True)
plt.legend()
plt.show()
# Convertir a radianes por segundo
rpm_rad = [x * (2 * 3.14159 / 60) for x in rpm]
# Guardar los datos de RPM en un nuevo CSV
df_rpm = pd.DataFrame({
    'time': time,
    'rpm': rpm,
    'rpm_rad': rpm_rad
})
df_rpm.to_csv('datos_rpm.csv', index=False)





        
