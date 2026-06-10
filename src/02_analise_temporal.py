from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import find_peaks

from audio_utils import carregar_audio, calcular_rms, calcular_tempo, ler_medicoes, salvar_csv
from config import AUDIO_DIR, GRAFICOS_DIR, MEDICOES_PATH, METRICAS_TEMPORAIS_PATH, preparar_pastas


GRAFICOS_TEMPORAIS_DIR = GRAFICOS_DIR / "02_temporal"


def contar_picos_temporais(sinal, taxa_amostragem):
    envoltoria = np.abs(sinal)

    altura_minima = np.mean(envoltoria) + (2 * np.std(envoltoria))
    distancia_minima = int(taxa_amostragem * 0.25)

    picos, propriedades = find_peaks(
        envoltoria,
        height=altura_minima,
        distance=distancia_minima,
    )

    return picos, propriedades, altura_minima


def gerar_grafico_temporal(sinal, taxa_amostragem, picos, caminho_saida: Path, titulo: str):
    tempo = calcular_tempo(sinal, taxa_amostragem)

    plt.figure(figsize=(12, 5))
    plt.plot(tempo, sinal, label="Sinal de áudio")

    if len(picos) > 0:
        plt.scatter(tempo[picos], sinal[picos], label="Picos detectados", s=18)

    plt.title(titulo)
    plt.xlabel("Tempo (s)")
    plt.ylabel("Amplitude relativa")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(caminho_saida, dpi=150)
    plt.close()


def executar():
    preparar_pastas()
    GRAFICOS_TEMPORAIS_DIR.mkdir(parents=True, exist_ok=True)

    medicoes = ler_medicoes(MEDICOES_PATH)
    resultados = []

    for _, medicao in medicoes.iterrows():
        id_medicao = medicao["id"]
        arquivo = medicao["arquivo"]
        caminho_audio = AUDIO_DIR / arquivo

        if not caminho_audio.exists():
            print(f"[ERRO] Arquivo não encontrado: {caminho_audio}")
            continue

        print(f"[OK] Análise temporal: {arquivo}")

        sinal, taxa_amostragem, _ = carregar_audio(caminho_audio)
        picos, _, altura_minima = contar_picos_temporais(sinal, taxa_amostragem)

        nome_base = Path(arquivo).stem
        caminho_grafico = GRAFICOS_TEMPORAIS_DIR / f"{nome_base}_temporal.png"

        gerar_grafico_temporal(
            sinal=sinal,
            taxa_amostragem=taxa_amostragem,
            picos=picos,
            caminho_saida=caminho_grafico,
            titulo=f"Análise temporal - Medição {id_medicao} - {arquivo}",
        )

        resultados.append({
            "id": id_medicao,
            "arquivo": arquivo,
            "rms": round(calcular_rms(sinal), 6),
            "amplitude_maxima_absoluta": round(float(np.max(np.abs(sinal))), 6),
            "quantidade_picos_detectados": int(len(picos)),
            "limiar_usado_para_picos": round(float(altura_minima), 6),
            "grafico_temporal": str(caminho_grafico),
        })

    resultados_df = pd.DataFrame(resultados)
    salvar_csv(resultados_df, METRICAS_TEMPORAIS_PATH)

    print("\nAnálise temporal finalizada.")
    print(f"Métricas salvas em: {METRICAS_TEMPORAIS_PATH}")
    print(f"Gráficos salvos em: {GRAFICOS_TEMPORAIS_DIR}")


if __name__ == "__main__":
    executar()
