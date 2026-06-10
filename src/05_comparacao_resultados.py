from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import find_peaks

from audio_utils import (
    carregar_audio,
    calcular_energia_media,
    calcular_rms,
    ler_medicoes,
    limitar_frequencia_maxima,
    salvar_csv,
)
from config import (
    AUDIO_DIR,
    COMPARACAO_RESULTADOS_PATH,
    GRAFICOS_DIR,
    MEDICOES_PATH,
    preparar_pastas,
)


GRAFICOS_COMPARACAO_DIR = GRAFICOS_DIR / "05_comparacao"


def calcular_fft(sinal, taxa_amostragem):
    quantidade_amostras = len(sinal)

    janela = np.hanning(quantidade_amostras)
    sinal_janelado = sinal * janela

    valores_fft = np.fft.rfft(sinal_janelado)
    frequencias = np.fft.rfftfreq(quantidade_amostras, d=1 / taxa_amostragem)
    magnitude = np.abs(valores_fft) / quantidade_amostras

    return frequencias, magnitude


def calcular_energia_faixa(frequencias, magnitude, inicio_hz, fim_hz):
    mascara = (frequencias >= inicio_hz) & (frequencias <= fim_hz)

    if not np.any(mascara):
        return 0.0

    return float(np.sum(magnitude[mascara] ** 2))


def calcular_frequencia_dominante(frequencias, magnitude):
    mascara = frequencias >= 20

    frequencias_validas = frequencias[mascara]
    magnitude_valida = magnitude[mascara]

    if len(frequencias_validas) == 0:
        return 0.0

    indice = np.argmax(magnitude_valida)

    return float(frequencias_validas[indice])


def contar_picos(sinal, taxa_amostragem):
    envoltoria = np.abs(sinal)

    altura_minima = np.mean(envoltoria) + (2 * np.std(envoltoria))
    distancia_minima = int(taxa_amostragem * 0.25)

    picos, _ = find_peaks(
        envoltoria,
        height=altura_minima,
        distance=distancia_minima,
    )

    return len(picos)


def gerar_grafico_barras(resultados_df, coluna, titulo, ylabel, nome_arquivo):
    caminho_saida = GRAFICOS_COMPARACAO_DIR / nome_arquivo

    plt.figure(figsize=(12, 5))
    plt.bar(resultados_df["arquivo"], resultados_df[coluna])
    plt.title(titulo)
    plt.xlabel("Áudio")
    plt.ylabel(ylabel)
    plt.xticks(rotation=20)
    plt.grid(axis="y")
    plt.tight_layout()
    plt.savefig(caminho_saida, dpi=150)
    plt.close()


def executar():
    preparar_pastas()
    GRAFICOS_COMPARACAO_DIR.mkdir(parents=True, exist_ok=True)

    medicoes = ler_medicoes(MEDICOES_PATH)
    resultados = []

    for _, medicao in medicoes.iterrows():
        id_medicao = medicao["id"]
        arquivo = medicao["arquivo"]
        caminho_audio = AUDIO_DIR / arquivo

        if not caminho_audio.exists():
            print(f"[ERRO] Arquivo não encontrado: {caminho_audio}")
            continue

        print(f"[OK] Comparando áudio: {arquivo}")

        sinal, taxa_amostragem, _ = carregar_audio(caminho_audio)

        frequencias, magnitude = calcular_fft(sinal, taxa_amostragem)
        freq_maxima_analise = limitar_frequencia_maxima(taxa_amostragem, 5000)

        resultados.append({
            "id": id_medicao,
            "arquivo": arquivo,
            "taxa_amostragem_hz": int(taxa_amostragem),
            "duracao_segundos": round(float(len(sinal) / taxa_amostragem), 2),
            "rms": round(calcular_rms(sinal), 6),
            "energia_media": round(calcular_energia_media(sinal), 6),
            "amplitude_maxima_absoluta": round(float(np.max(np.abs(sinal))), 6),
            "quantidade_picos": int(contar_picos(sinal, taxa_amostragem)),
            "frequencia_dominante_hz": round(calcular_frequencia_dominante(frequencias, magnitude), 2),
            "energia_20_250hz": round(calcular_energia_faixa(frequencias, magnitude, 20, 250), 8),
            "energia_250_2000hz": round(calcular_energia_faixa(frequencias, magnitude, 250, 2000), 8),
            "energia_2000_5000hz": round(calcular_energia_faixa(frequencias, magnitude, 2000, freq_maxima_analise), 8),
        })

    resultados_df = pd.DataFrame(resultados)
    salvar_csv(resultados_df, COMPARACAO_RESULTADOS_PATH)

    if resultados_df.empty:
        print("Nenhum resultado para comparar.")
        return

    gerar_grafico_barras(
        resultados_df,
        coluna="rms",
        titulo="Comparativo de RMS entre as medições",
        ylabel="RMS",
        nome_arquivo="comparativo_rms.png",
    )

    gerar_grafico_barras(
        resultados_df,
        coluna="energia_media",
        titulo="Comparativo de energia média entre as medições",
        ylabel="Energia média",
        nome_arquivo="comparativo_energia_media.png",
    )

    gerar_grafico_barras(
        resultados_df,
        coluna="quantidade_picos",
        titulo="Comparativo de quantidade de picos entre as medições",
        ylabel="Quantidade de picos",
        nome_arquivo="comparativo_picos.png",
    )

    gerar_grafico_barras(
        resultados_df,
        coluna="frequencia_dominante_hz",
        titulo="Comparativo de frequência dominante entre as medições",
        ylabel="Frequência dominante (Hz)",
        nome_arquivo="comparativo_frequencia_dominante.png",
    )

    print("\nComparação finalizada.")
    print(f"Resultados salvos em: {COMPARACAO_RESULTADOS_PATH}")
    print(f"Gráficos salvos em: {GRAFICOS_COMPARACAO_DIR}")


if __name__ == "__main__":
    executar()
