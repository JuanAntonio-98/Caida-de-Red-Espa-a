import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Cargar CSV
df = pd.read_csv("apagón_datos.csv", sep=";", encoding="utf-8")
df['Hora'] = pd.to_datetime(df['Hora'], format='%H:%M')

# Fuentes de generación
fuentes = ['Nuclear', 'Carbón', 'Ciclo combinado', 'Cogeneración y Residuos',
           'Hidráulica', 'Solar FV', 'Solar térmica', 'Eólica', 'Turbinación bombeo', 'Térmica renovable']

# Consumos y exportaciones
otros = ['Consumo bombeo', 'Consumo baterías', 'Baterías', 'Enlace Balear',
         'Francia exportación', 'Portugal exportación', 'Marruecos exportación', 'Andorra exportación']

# Colores para gráficas
colores = {
    'Nuclear': 'red', 'Carbón': 'black', 'Ciclo combinado': 'blue',
    'Cogeneración y Residuos': 'purple', 'Hidráulica': 'aqua',
    'Solar FV': 'orange', 'Solar térmica': 'gold', 'Eólica': 'green',
    'Turbinación bombeo':'pink', 'Térmica renovable':'Navy'
}

# Graficar producción por fuente
plt.figure(figsize=(12, 6))
for fuente in fuentes:
    plt.plot(df['Hora'], df[fuente], marker='o', label=fuente, color=colores.get(fuente, 'gray'))
plt.title("Producción por fuente de energía durante el apagón")
plt.xlabel("Hora")
plt.ylabel("Producción (MW)")
plt.grid(True)
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("produccion_apagon.png")
plt.show()

print("\n--- ANÁLISIS DEL CAMBIO ENTRE 12:30 Y 12:35 ---")

hora1 = datetime.strptime("12:30", "%H:%M")
hora2 = datetime.strptime("12:35", "%H:%M")
t1 = df[df['Hora'] == hora1]
t2 = df[df['Hora'] == hora2]

if not t1.empty and not t2.empty:
    t1 = t1.iloc[0]
    t2 = t2.iloc[0]

    # 1. Tabla de generación
    diferencias = {}
    total_mw_antes = 0
    total_mw_dif = 0

    for fuente in fuentes:
        mw_antes = t1[fuente]
        mw_despues = t2[fuente]
        diff = mw_despues - mw_antes
        porcentaje = (diff / mw_antes * 100) if mw_antes != 0 else 0
        if diff != 0:
            diferencias[fuente] = {"MW": diff, "%": porcentaje}
        total_mw_antes += mw_antes
        total_mw_dif += diff

    porcentaje_total = (total_mw_dif / total_mw_antes * 100) if total_mw_antes != 0 else 0
    diferencias_ordenadas = dict(sorted(diferencias.items(), key=lambda x: x[1]["MW"]))

    print(f"{'Fuente':<25}{'Δ MW':>10}{'% Cambio':>12}")
    print("-" * 50)
    for fuente, datos in diferencias_ordenadas.items():
        print(f"{fuente:<25}{datos['MW']:>10.0f}{datos['%']:>11.1f} %")
    print("-" * 50)
    print(f"{'Total':<25}{total_mw_dif:>10.0f}{porcentaje_total:>11.1f} %")

    # 2. Gráfica comparación generación vs exportaciones
    gen_total = df[fuentes].sum(axis=1)
    export_total = df[['Francia exportación', 'Portugal exportación', 'Marruecos exportación', 'Andorra exportación']].sum(axis=1)

    plt.figure(figsize=(10, 5))
    plt.plot(df['Hora'], gen_total, marker='o', label='Generación total', color='blue')
    plt.plot(df['Hora'], export_total, marker='o', label='Exportaciones totales', color='red')
    plt.title("Comparación de Generación vs Exportaciones")
    plt.xlabel("Hora")
    plt.ylabel("Potencia (MW)")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("comparacion_gen_exportaciones.png")
    plt.show()

else:
    print("❌ No se encontraron registros para una de las horas.")

# --- ANÁLISIS DE VARIACIONES EN CONSUMOS Y EXPORTACIONES ---


variaciones_consumo = {}
total_mw_otros_antes = 0
total_mw_otros_dif = 0

for fuente in otros:
    mw_antes = t1[fuente]
    mw_despues = t2[fuente]
    diferencia = mw_despues - mw_antes
    if mw_antes != 0:
        porcentaje = (diferencia / mw_antes) * 100
    else:
        porcentaje = float('inf') if diferencia != 0 else 0

    if diferencia != 0:
        variaciones_consumo[fuente] = {
            "MW": diferencia,
            "%": porcentaje
        }

    total_mw_otros_antes += mw_antes
    total_mw_otros_dif += diferencia

porcentaje_total_otros = (total_mw_otros_dif / total_mw_otros_antes) * 100 if total_mw_otros_antes != 0 else 0

print("\n--- VARIACIÓN EN CONSUMO Y EXPORTACIONES ENTRE 12:30 Y 12:35 ---")
print(f"{'Concepto':<25}{'Δ MW':>10}{'% Cambio':>12}")
print("-" * 50)
for fuente, datos in variaciones_consumo.items():
    print(f"{fuente:<25}{datos['MW']:>10.0f}{datos['%']:>11.1f} %")
print("-" * 50)
print(f"{'Total':<25}{total_mw_otros_dif:>10.0f}{porcentaje_total_otros:>11.1f} %")

# --- GRÁFICO COMPARATIVO ENTRE EXPORTACIONES Y GENERACIÓN ---
t1_gen_total = t1[fuentes].sum()
t2_gen_total = t2[fuentes].sum()
t1_exp_total = t1[['Francia exportación', 'Portugal exportación', 'Marruecos exportación', 'Andorra exportación']].sum()
t2_exp_total = t2[['Francia exportación', 'Portugal exportación', 'Marruecos exportación', 'Andorra exportación']].sum()

variacion_gen = t2_gen_total - t1_gen_total
variacion_exp = t2_exp_total - t1_exp_total

plt.figure(figsize=(8, 6))
plt.bar(['Generación', 'Exportaciones'], [variacion_gen, variacion_exp], color=['blue', 'red'])
plt.title("Variaciones netas entre 12:30 y 12:35")
plt.ylabel("Δ MW")
plt.grid(axis='y')
plt.tight_layout()
plt.savefig("comparacion_gen_export.png")
plt.show()

# --- ANÁLISIS PORCENTUAL DE EXPORTACIÓN ---
porc_export_1230 = (t1_exp_total / t1_gen_total) * 100 if t1_gen_total != 0 else 0
porc_export_1235 = (t2_exp_total / t2_gen_total) * 100 if t2_gen_total != 0 else 0

print("\n--- PORCENTAJE EXPORTADO RESPECTO A LA GENERACIÓN ---")
print(f"A las 12:30: {porc_export_1230:.2f} % de la generación fue exportada")
print(f"A las 12:35: {porc_export_1235:.2f} % de la generación fue exportada")
