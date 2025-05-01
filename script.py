import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Cargar CSV

df = pd.read_csv("apagón_datos.csv", sep=";", encoding="utf-8")
df['Hora'] = pd.to_datetime(df['Hora'], format='%H:%M')

# --- CATEGORIZACIÓN DE VARIABLES ---

# Fuentes de generación (producción de energía)
fuentes = ['Nuclear', 'Carbón', 'Ciclo combinado', 'Cogeneración y Residuos',
           'Hidráulica', 'Solar FV', 'Solar térmica', 'Eólica', 'Turbinación bombeo', 'Térmica renovable']

# Almacenamiento y enlace Balear (consumos internos del sistema)
almacenamiento = ['Consumo bombeo', 'Consumo baterías', 'Baterías', 'Enlace Balear']

# Exportaciones (salida del sistema a otros países)
exportaciones = ['Francia exportación', 'Portugal exportación', 'Marruecos exportación', 'Andorra exportación']

# Colores para gráficas
colores = {
    'Nuclear': 'red', 'Carbón': 'black', 'Ciclo combinado': 'blue',
    'Cogeneración y Residuos': 'purple', 'Hidráulica': 'aqua',
    'Solar FV': 'orange', 'Solar térmica': 'gold', 'Eólica': 'green',
    'Turbinación bombeo':'pink', 'Térmica renovable':'Navy'
}

# --- GRÁFICO PRODUCCIÓN POR FUENTE ---
plt.figure(figsize=(14, 7))
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

# --- ANÁLISIS PUNTUAL ENTRE 12:30 Y 12:35 ---

hora1 = datetime.strptime("12:30", "%H:%M")
hora2 = datetime.strptime("12:35", "%H:%M")
t1 = df[df['Hora'] == hora1]
t2 = df[df['Hora'] == hora2]

if not t1.empty and not t2.empty:
    t1 = t1.iloc[0]
    t2 = t2.iloc[0]

    print("\n--- VARIACIÓN EN FUENTES DE GENERACIÓN ---")
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

    # Fuente más afectada
    fuente_mas_afectada = min(diferencias_ordenadas.items(), key=lambda x: x[1]["MW"])
    print(f"\nLa fuente más afectada fue: {fuente_mas_afectada[0]} ({fuente_mas_afectada[1]['MW']} MW)")

    # Exportación más afectada
    export_variaciones = {
        ex: t2[ex] - t1[ex] for ex in exportaciones
    }
    export_mas_afectada = max(export_variaciones.items(), key=lambda x: x[1])
    print(f"La exportación más afectada fue: {export_mas_afectada[0]} ({export_mas_afectada[1]} MW)")

    # Total generación y total exportaciones
    gen_total = df[fuentes].sum(axis=1)
    export_total = df[exportaciones].sum(axis=1)

    # Gráfico de generación vs exportaciones
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

    # --- VARIACIÓN EN ALMACENAMIENTO Y EXPORTACIONES ---

    print("\n--- VARIACIÓN EN ALMACENAMIENTO Y EXPORTACIONES ENTRE 12:30 Y 12:35 ---")
    otros = almacenamiento + exportaciones
    variaciones_otros = {}
    total_mw_otros_antes = 0
    total_mw_otros_dif = 0

    for fuente in otros:
        mw_antes = t1[fuente]
        mw_despues = t2[fuente]
        diferencia = mw_despues - mw_antes
        porcentaje = (diferencia / mw_antes * 100) if mw_antes != 0 else 0
        if diferencia != 0:
            variaciones_otros[fuente] = {"MW": diferencia, "%": porcentaje}
        total_mw_otros_antes += mw_antes
        total_mw_otros_dif += diferencia

    porcentaje_total_otros = (total_mw_otros_dif / total_mw_otros_antes * 100) if total_mw_otros_antes != 0 else 0

    print(f"{'Concepto':<25}{'Δ MW':>10}{'% Cambio':>12}")
    print("-" * 50)
    for fuente, datos in variaciones_otros.items():
        print(f"{fuente:<25}{datos['MW']:>10.0f}{datos['%']:>11.1f} %")
    print("-" * 50)
    print(f"{'Total':<25}{total_mw_otros_dif:>10.0f}{porcentaje_total_otros:>11.1f} %")

    # --- VARIACIÓN GLOBAL EXPORTACIONES VS GENERACIÓN ---

    t1_gen_total = t1[fuentes].sum()
    t2_gen_total = t2[fuentes].sum()
    t1_exp_total = t1[exportaciones].sum()
    t2_exp_total = t2[exportaciones].sum()

    variacion_gen = t2_gen_total - t1_gen_total
    variacion_exp = t2_exp_total - t1_exp_total

    cambio_porc_export_vs_gen = (variacion_exp / variacion_gen * 100) if variacion_gen != 0 else 0
    print(f"\nCambio porcentual global de exportaciones respecto a generación: {cambio_porc_export_vs_gen:.2f} %")

    # --- DESAJUSTE ENTRE GENERACIÓN Y CONSUMO ---

    demanda_real_t1 = t1['Total demanda real']
    demanda_real_t2 = t2['Total demanda real']

    consumo_total_t1 = demanda_real_t1 + abs(t1[almacenamiento + exportaciones].sum())
    consumo_total_t2 = demanda_real_t2 + abs(t2[almacenamiento + exportaciones].sum())

    uso_gen_t1 = consumo_total_t1 / t1_gen_total * 100 if t1_gen_total != 0 else 0
    uso_gen_t2 = consumo_total_t2 / t2_gen_total * 100 if t2_gen_total != 0 else 0

    print("\n--- USO DE GENERACIÓN TOTAL ---")
    print(f"A las 12:30: {uso_gen_t1:.2f} % de la generación fue destinada a consumo/exportaciones")
    print(f"A las 12:35: {uso_gen_t2:.2f} % de la generación fue destinada a consumo/exportaciones")

    # --- GRÁFICO DE PORCENTAJES ENERGÉTICOS ---
    plt.figure(figsize=(10, 6))
    etiquetas = fuentes + almacenamiento + exportaciones
    valores_t1 = [t1[e] for e in etiquetas]
    total_t1 = sum(valores_t1)
    porcentajes_t1 = [v / total_t1 * 100 if total_t1 != 0 else 0 for v in valores_t1]

    plt.barh(etiquetas, porcentajes_t1, color='skyblue')
    plt.title("Distribución porcentual de energía a las 12:30")
    plt.xlabel("% sobre el total")
    plt.tight_layout()
    plt.savefig("porcentajes_energia_1230.png")
    plt.show()

else:
    print("\n❌ No se encontraron registros para una de las horas.")
