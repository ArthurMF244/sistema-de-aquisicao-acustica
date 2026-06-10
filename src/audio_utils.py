from pathlib import Path

import numpy as np
import pandas as pd
from scipy.io import wavfile


def ler_medicoes(caminho_csv: Path) -> pd.DataFrame:
    if not caminho_csv.exists():
        raise FileNotFoundError(f"Arquivo de medições não encontrado: {caminho_csv}")

    medicoes = pd.read_csv(caminho_csv)

    colunas_obrigatorias = {"id", "arquivo"}
    colunas_ausentes = colunas_obrigatorias - set(medicoes.columns)

    if colunas_ausentes:
        raise ValueError(f"Colunas ausentes no CSV: {colunas_ausentes}")

    return medicoes


def converter_pcm_para_float(sinal: np.ndarray) -> np.ndarray:
    """
    Converte o áudio para float entre aproximadamente -1 e 1.

    Importante:
    Aqui NÃO normalizamos cada áudio pelo maior pico dele.
    Isso preserva melhor a diferença de intensidade entre as medições.
    """
    if np.issubdtype(sinal.dtype, np.floating):
        return sinal.astype(np.float32)

    if sinal.dtype == np.uint8:
        return ((sinal.astype(np.float32) - 128) / 128)

    info = np.iinfo(sinal.dtype)
    maior_valor = max(abs(info.min), abs(info.max))

    return sinal.astype(np.float32) / maior_valor


def carregar_audio(caminho_audio: Path):
    if not caminho_audio.exists():
        raise FileNotFoundError(f"Áudio não encontrado: {caminho_audio}")

    taxa_amostragem, sinal = wavfile.read(caminho_audio)

    canais_originais = 1

    if sinal.ndim > 1:
        canais_originais = sinal.shape[1]
        sinal = sinal.mean(axis=1)

    sinal = converter_pcm_para_float(sinal)

    return sinal, taxa_amostragem, canais_originais


def calcular_tempo(sinal: np.ndarray, taxa_amostragem: int) -> np.ndarray:
    return np.arange(len(sinal)) / taxa_amostragem


def calcular_rms(sinal: np.ndarray) -> float:
    return float(np.sqrt(np.mean(sinal ** 2)))


def calcular_energia_media(sinal: np.ndarray) -> float:
    return float(np.mean(sinal ** 2))


def nome_base_arquivo(arquivo: str) -> str:
    return Path(arquivo).stem


def limitar_frequencia_maxima(taxa_amostragem: int, frequencia_desejada: float = 5000) -> float:
    nyquist = taxa_amostragem / 2
    return min(frequencia_desejada, nyquist * 0.95)


def salvar_csv(dataframe: pd.DataFrame, caminho_saida: Path):
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(caminho_saida, index=False)
