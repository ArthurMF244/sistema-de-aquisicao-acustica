import numpy as np
import pandas as pd

from audio_utils import carregar_audio, calcular_rms, ler_medicoes, salvar_csv
from config import AUDIO_DIR, BASE_AUDIOS_PATH, MEDICOES_PATH, preparar_pastas


def calcular_informacoes_basicas(sinal, taxa_amostragem, canais_originais):
    quantidade_amostras = len(sinal)
    duracao_segundos = quantidade_amostras / taxa_amostragem

    return {
        "taxa_amostragem_hz": int(taxa_amostragem),
        "canais_originais": int(canais_originais),
        "quantidade_amostras": int(quantidade_amostras),
        "duracao_segundos": round(float(duracao_segundos), 2),
        "amplitude_minima": round(float(np.min(sinal)), 6),
        "amplitude_maxima": round(float(np.max(sinal)), 6),
        "amplitude_media_absoluta": round(float(np.mean(np.abs(sinal))), 6),
        "rms": round(calcular_rms(sinal), 6),
    }


def executar():
    preparar_pastas()

    medicoes = ler_medicoes(MEDICOES_PATH)
    resultados = []

    for _, medicao in medicoes.iterrows():
        id_medicao = medicao["id"]
        arquivo = medicao["arquivo"]
        caminho_audio = AUDIO_DIR / arquivo

        if not caminho_audio.exists():
            print(f"[ERRO] Arquivo não encontrado: {caminho_audio}")

            resultados.append({
                "id": id_medicao,
                "arquivo": arquivo,
                "status": "arquivo_nao_encontrado",
            })

            continue

        print(f"[OK] Lendo áudio: {arquivo}")

        sinal, taxa_amostragem, canais_originais = carregar_audio(caminho_audio)

        resultados.append({
            "id": id_medicao,
            "arquivo": arquivo,
            "status": "processado",
            **calcular_informacoes_basicas(sinal, taxa_amostragem, canais_originais),
        })

    resultados_df = pd.DataFrame(resultados)
    salvar_csv(resultados_df, BASE_AUDIOS_PATH)

    print("\nBase de dados acústicos criada com sucesso.")
    print(f"Arquivo gerado: {BASE_AUDIOS_PATH}")


if __name__ == "__main__":
    executar()
