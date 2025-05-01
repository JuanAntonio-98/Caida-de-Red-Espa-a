import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Cargar CSV
df = pd.read_csv("apagón_datos.csv", sep=";", encoding="utf-8")

# Convertir la columna 'Hora' en datetime (añadiendo una fecha dummy)
df['Hora'] = pd.to_datetime(df['Hora'], format='%H:%M')

# Lista de fuentes clave para analizar
fuentes = ['Nuclear', 'Carbón', 'Ciclo combinado', 'Cogeneración y Residuos',
           'Hidráulica', 'Solar FV', 'Solar térmica', 'Eólica']

# Diccionario de colores por fuente (puedes personalizar)
colores = {
    'Nuclear': 'red',
    'Carbón': 'black',
    'Ciclo combinado': 'blue',
    'Cogeneración y Residuos': 'purple',
    'Hidráulica': 'aqua',
    'Solar FV': 'orange',
    'Solar térmica': 'gold',
    'Eólica': 'green'
}

# Graficar cada fuente
plt.figure(figsize=(12, 6))
for fuente in fuentes:
    plt.plot(df['Hora'], df[fuente], marker='o', label=fuente, color=colores.get(fuente, 'gray'))

# Estética
plt.title("Producción por fuente de energía durante el apagón")
plt.xlabel("Hora")
plt.ylabel("Producción (MW)")
plt.grid(True)
plt.legend()
plt.xticks(rotation=45)

# Mostrar o guardar
plt.tight_layout()
plt.savefig("produccion_apagon.png")  # Guarda en archivo PNG
plt.show()


print("\n--- ANÁLISIS DEL CAMBIO ENTRE 12:30 Y 12:35 ---")

# Buscar las filas de 12:30 y 12:35
hora1 = datetime.strptime("12:30", "%H:%M")
hora2 = datetime.strptime("12:35", "%H:%M")
t1 = df[df['Hora'] == hora1]
t2 = df[df['Hora'] == hora2]

if not t1.empty and not t2.empty:
    t1 = t1.iloc[0]
    t2 = t2.iloc[0]

    diferencias = {}
    total_mw_antes = 0
    total_mw_dif = 0

    for fuente in fuentes:
        mw_antes = t1[fuente]
        mw_despues = t2[fuente]
        diferencia = mw_despues - mw_antes
        if mw_antes != 0:
            porcentaje = (diferencia / mw_antes) * 100
        else:
            porcentaje = float('inf') if diferencia != 0 else 0

        if diferencia != 0:
            diferencias[fuente] = {
                "MW": diferencia,
                "%": porcentaje
            }

        total_mw_antes += mw_antes
        total_mw_dif += diferencia

    porcentaje_total = (total_mw_dif / total_mw_antes) * 100 if total_mw_antes != 0 else 0

    # Ordenar de mayor a menor pérdida en MW
    diferencias_ordenadas = dict(sorted(diferencias.items(), key=lambda x: x[1]["MW"]))

    print(f"{'Fuente':<25}{'Δ MW':>10}{'% Cambio':>12}")
    print("-" * 50)
    for fuente, datos in diferencias_ordenadas.items():
        print(f"{fuente:<25}{datos['MW']:>10.0f}{datos['%']:>11.1f} %")
    print("-" * 50)
    print(f"{'Total':<25}{total_mw_dif:>10.0f}{porcentaje_total:>11.1f} %")
else:
    print("❌ No se encontraron registros para una de las horas.")
