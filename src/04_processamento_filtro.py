from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.io import wavfile
from scipy.signal import butter, filtfilt

from audio_utils import carregar_audio, calcular_rms, calcular_tempo, ler_medicoes, salvar_csv
from config import (
    AUDIO_DIR,
    AUDIO_PROCESSADO_DIR,
    FILTRO_RESULTADOS_PATH,
    GRAFICOS_DIR,
    MEDICOES_PATH,
    preparar_pastas,
)


GRAFICOS_FILTRO_DIR = GRAFICOS_DIR / "04_filtro"


def aplicar_filtro_passa_faixa(
    sinal,
    taxa_amostragem,
    frequencia_minima=50,
    frequencia_maxima=5000,
    ordem=4,
):
    nyquist = taxa_amostragem / 2

    frequencia_minima_ajustada = max(frequencia_minima, 1)
    frequencia_maxima_ajustada = min(frequencia_maxima, nyquist * 0.95)

    if frequencia_minima_ajustada >= frequencia_maxima_ajustada:
        return sinal, frequencia_minima_ajustada, frequencia_maxima_ajustada, "filtro_ignorado"

    frequencia_minima_normalizada = frequencia_minima_ajustada / nyquist
    frequencia_maxima_normalizada = frequencia_maxima_ajustada / nyquist

    b, a = butter(
        ordem,
        [frequencia_minima_normalizada, frequencia_maxima_normalizada],
        btype="band",
    )

    sinal_filtrado = filtfilt(b, a, sinal)

    return (
        sinal_filtrado,
        frequencia_minima_ajustada,
        frequencia_maxima_ajustada,
        "filtro_aplicado",
    )


def gerar_grafico_original_filtrado(
    sinal_original,
    sinal_filtrado,
    taxa_amostragem,
    caminho_saida: Path,
    titulo: str,
):
    tempo = calcular_tempo(sinal_original, taxa_amostragem)

    plt.figure(figsize=(12, 5))
    plt.plot(tempo, sinal_original, label="Original", alpha=0.7)
    plt.plot(tempo, sinal_filtrado, label="Filtrado", alpha=0.7)
    plt.title(titulo)
    plt.xlabel("Tempo (s)")
    plt.ylabel("Amplitude relativa")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(caminho_saida, dpi=150)
    plt.close()


def salvar_wav_filtrado(sinal_filtrado, taxa_amostragem, caminho_saida: Path):
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)

    sinal_limitado = np.clip(sinal_filtrado, -1, 1)
    sinal_int16 = (sinal_limitado * 32767).astype(np.int16)

    wavfile.write(caminho_saida, taxa_amostragem, sinal_int16)


def executar():
    preparar_pastas()
    GRAFICOS_FILTRO_DIR.mkdir(parents=True, exist_ok=True)

    medicoes = ler_medicoes(MEDICOES_PATH)
    resultados = []

    for _, medicao in medicoes.iterrows():
        id_medicao = medicao["id"]
        arquivo = medicao["arquivo"]
        caminho_audio = AUDIO_DIR / arquivo

        if not caminho_audio.exists():
            print(f"[ERRO] Arquivo não encontrado: {caminho_audio}")
            continue

        print(f"[OK] Aplicando filtro: {arquivo}")

        sinal, taxa_amostragem, _ = carregar_audio(caminho_audio)

        sinal_filtrado, freq_min, freq_max, status = aplicar_filtro_passa_faixa(
            sinal=sinal,
            taxa_amostragem=taxa_amostragem,
            frequencia_minima=50,
            frequencia_maxima=5000,
            ordem=4,
        )

        nome_base = Path(arquivo).stem

        caminho_grafico = GRAFICOS_FILTRO_DIR / f"{nome_base}_original_vs_filtrado.png"
        caminho_audio_filtrado = AUDIO_PROCESSADO_DIR / f"{nome_base}_filtrado.wav"

        gerar_grafico_original_filtrado(
            sinal_original=sinal,
            sinal_filtrado=sinal_filtrado,
            taxa_amostragem=taxa_amostragem,
            caminho_saida=caminho_grafico,
            titulo=f"Original x filtrado - Medição {id_medicao} - {arquivo}",
        )

        salvar_wav_filtrado(sinal_filtrado, taxa_amostragem, caminho_audio_filtrado)

        resultados.append({
            "id": id_medicao,
            "arquivo": arquivo,
            "status": status,
            "frequencia_minima_aplicada_hz": round(float(freq_min), 2),
            "frequencia_maxima_aplicada_hz": round(float(freq_max), 2),
            "rms_original": round(calcular_rms(sinal), 6),
            "rms_filtrado": round(calcular_rms(sinal_filtrado), 6),
            "audio_filtrado": str(caminho_audio_filtrado),
            "grafico_filtro": str(caminho_grafico),
        })

    resultados_df = pd.DataFrame(resultados)
    salvar_csv(resultados_df, FILTRO_RESULTADOS_PATH)

    print("\nProcessamento por filtro finalizado.")
    print(f"Resultados salvos em: {FILTRO_RESULTADOS_PATH}")
    print(f"Áudios filtrados salvos em: {AUDIO_PROCESSADO_DIR}")
    print(f"Gráficos salvos em: {GRAFICOS_FILTRO_DIR}")


if __name__ == "__main__":
    executar()
