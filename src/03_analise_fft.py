from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from audio_utils import carregar_audio, ler_medicoes, limitar_frequencia_maxima, salvar_csv
from config import AUDIO_DIR, FFT_RESULTADOS_PATH, GRAFICOS_DIR, MEDICOES_PATH, preparar_pastas


GRAFICOS_FFT_DIR = GRAFICOS_DIR / "03_fft"


def calcular_fft(sinal, taxa_amostragem):
    quantidade_amostras = len(sinal)

    janela = np.hanning(quantidade_amostras)
    sinal_janelado = sinal * janela

    valores_fft = np.fft.rfft(sinal_janelado)
    frequencias = np.fft.rfftfreq(quantidade_amostras, d=1 / taxa_amostragem)

    magnitude = np.abs(valores_fft) / quantidade_amostras

    return frequencias, magnitude


def obter_frequencias_dominantes(frequencias, magnitude, quantidade=5):
    mascara = frequencias >= 20

    frequencias_validas = frequencias[mascara]
    magnitude_valida = magnitude[mascara]

    if len(frequencias_validas) == 0:
        return []

    indices = np.argsort(magnitude_valida)[-quantidade:][::-1]

    dominantes = []

    for indice in indices:
        dominantes.append({
            "frequencia_hz": round(float(frequencias_validas[indice]), 2),
            "magnitude": round(float(magnitude_valida[indice]), 8),
        })

    return dominantes


def gerar_grafico_fft(frequencias, magnitude, taxa_amostragem, caminho_saida: Path, titulo: str):
    limite_x = limitar_frequencia_maxima(taxa_amostragem, 5000)

    plt.figure(figsize=(12, 5))
    plt.plot(frequencias, magnitude)
    plt.title(titulo)
    plt.xlabel("Frequência (Hz)")
    plt.ylabel("Magnitude")
    plt.xlim(0, limite_x)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(caminho_saida, dpi=150)
    plt.close()


def executar():
    preparar_pastas()
    GRAFICOS_FFT_DIR.mkdir(parents=True, exist_ok=True)

    medicoes = ler_medicoes(MEDICOES_PATH)
    resultados = []

    for _, medicao in medicoes.iterrows():
        id_medicao = medicao["id"]
        arquivo = medicao["arquivo"]
        caminho_audio = AUDIO_DIR / arquivo

        if not caminho_audio.exists():
            print(f"[ERRO] Arquivo não encontrado: {caminho_audio}")
            continue

        print(f"[OK] Análise FFT: {arquivo}")

        sinal, taxa_amostragem, _ = carregar_audio(caminho_audio)

        frequencias, magnitude = calcular_fft(sinal, taxa_amostragem)
        dominantes = obter_frequencias_dominantes(frequencias, magnitude, quantidade=5)

        nome_base = Path(arquivo).stem
        caminho_grafico = GRAFICOS_FFT_DIR / f"{nome_base}_fft.png"

        gerar_grafico_fft(
            frequencias=frequencias,
            magnitude=magnitude,
            taxa_amostragem=taxa_amostragem,
            caminho_saida=caminho_grafico,
            titulo=f"FFT - Medição {id_medicao} - {arquivo}",
        )

        for posicao, item in enumerate(dominantes, start=1):
            resultados.append({
                "id": id_medicao,
                "arquivo": arquivo,
                "posicao": posicao,
                "frequencia_dominante_hz": item["frequencia_hz"],
                "magnitude": item["magnitude"],
                "grafico_fft": str(caminho_grafico),
            })

    resultados_df = pd.DataFrame(resultados)
    salvar_csv(resultados_df, FFT_RESULTADOS_PATH)

    print("\nAnálise FFT finalizada.")
    print(f"Frequências dominantes salvas em: {FFT_RESULTADOS_PATH}")
    print(f"Gráficos salvos em: {GRAFICOS_FFT_DIR}")


if __name__ == "__main__":
    executar()
