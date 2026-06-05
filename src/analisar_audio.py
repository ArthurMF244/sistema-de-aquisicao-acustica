from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.io import wavfile
from scipy.signal import butter, filtfilt, find_peaks, spectrogram


BASE_DIR = Path(__file__).resolve().parent.parent

AUDIO_DIR = BASE_DIR / "audios" / "wav"
DADOS_DIR = BASE_DIR / "dados"
GRAFICOS_DIR = BASE_DIR / "graficos"

DADOS_PATH = DADOS_DIR / "medicoes.csv"
RESULTADOS_PATH = DADOS_DIR / "resultados_audio.csv"

GRAFICOS_DIR.mkdir(parents=True, exist_ok=True)


def carregar_audio(caminho_audio: Path):
    taxa_amostragem, sinal = wavfile.read(caminho_audio)

    if sinal.ndim > 1:
        sinal = sinal.mean(axis=1)

    sinal = sinal.astype(np.float32)

    maior_valor = np.max(np.abs(sinal))

    if maior_valor > 0:
        sinal = sinal / maior_valor

    return sinal, taxa_amostragem


def calcular_tempo(sinal, taxa_amostragem):
    return np.arange(len(sinal)) / taxa_amostragem


def gerar_grafico_tempo(sinal, taxa_amostragem, caminho_saida: Path, titulo: str):
    tempo = calcular_tempo(sinal, taxa_amostragem)

    plt.figure(figsize=(12, 5))
    plt.plot(tempo, sinal)
    plt.title(titulo)
    plt.xlabel("Tempo (s)")
    plt.ylabel("Amplitude normalizada")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(caminho_saida, dpi=150)
    plt.close()


def calcular_fft(sinal, taxa_amostragem):
    quantidade_amostras = len(sinal)

    janela = np.hanning(quantidade_amostras)
    sinal_janelado = sinal * janela

    fft = np.fft.rfft(sinal_janelado)
    frequencias = np.fft.rfftfreq(quantidade_amostras, d=1 / taxa_amostragem)
    magnitude = np.abs(fft)

    return frequencias, magnitude


def gerar_grafico_fft(sinal, taxa_amostragem, caminho_saida: Path, titulo: str):
    frequencias, magnitude = calcular_fft(sinal, taxa_amostragem)

    plt.figure(figsize=(12, 5))
    plt.plot(frequencias, magnitude)
    plt.title(titulo)
    plt.xlabel("Frequência (Hz)")
    plt.ylabel("Magnitude")
    plt.xlim(0, 5000)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(caminho_saida, dpi=150)
    plt.close()

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
        print(
            f"Filtro ignorado: faixa inválida para taxa de amostragem "
            f"{taxa_amostragem} Hz."
        )
        return sinal

    frequencia_minima_normalizada = frequencia_minima_ajustada / nyquist
    frequencia_maxima_normalizada = frequencia_maxima_ajustada / nyquist

    b, a = butter(
        ordem,
        [frequencia_minima_normalizada, frequencia_maxima_normalizada],
        btype="band",
    )

    sinal_filtrado = filtfilt(b, a, sinal)

    return sinal_filtrado

def gerar_grafico_comparativo_filtro(
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
    plt.ylabel("Amplitude normalizada")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(caminho_saida, dpi=150)
    plt.close()


def gerar_espectrograma(sinal, taxa_amostragem, caminho_saida: Path, titulo: str):
    frequencias, tempos, intensidade = spectrogram(
        sinal,
        fs=taxa_amostragem,
        nperseg=1024,
        noverlap=512,
    )

    intensidade_db = 10 * np.log10(intensidade + 1e-10)

    plt.figure(figsize=(12, 5))
    plt.pcolormesh(tempos, frequencias, intensidade_db, shading="gouraud")
    plt.title(titulo)
    plt.xlabel("Tempo (s)")
    plt.ylabel("Frequência (Hz)")
    plt.ylim(0, 5000)
    plt.colorbar(label="Intensidade (dB relativo)")
    plt.tight_layout()
    plt.savefig(caminho_saida, dpi=150)
    plt.close()


def calcular_metricas(sinal, taxa_amostragem):
    amplitude_media = np.mean(np.abs(sinal))
    amplitude_maxima = np.max(np.abs(sinal))
    energia_media = np.mean(sinal ** 2)
    rms = np.sqrt(np.mean(sinal ** 2))

    frequencias, magnitude = calcular_fft(sinal, taxa_amostragem)

    indice_frequencia_dominante = np.argmax(magnitude[1:]) + 1
    frequencia_dominante = frequencias[indice_frequencia_dominante]

    energia_baixa = calcular_energia_faixa(frequencias, magnitude, 20, 250)
    energia_media_faixa = calcular_energia_faixa(frequencias, magnitude, 250, 2000)
    energia_alta = calcular_energia_faixa(frequencias, magnitude, 2000, 5000)

    quantidade_picos = contar_picos_relevantes(sinal)

    return {
        "amplitude_media": round(float(amplitude_media), 6),
        "amplitude_maxima": round(float(amplitude_maxima), 6),
        "energia_media": round(float(energia_media), 6),
        "rms": round(float(rms), 6),
        "frequencia_dominante_hz": round(float(frequencia_dominante), 2),
        "energia_20_250hz": round(float(energia_baixa), 6),
        "energia_250_2000hz": round(float(energia_media_faixa), 6),
        "energia_2000_5000hz": round(float(energia_alta), 6),
        "quantidade_picos": int(quantidade_picos),
    }


def calcular_energia_faixa(frequencias, magnitude, inicio_hz, fim_hz):
    mascara = (frequencias >= inicio_hz) & (frequencias <= fim_hz)

    if not np.any(mascara):
        return 0

    return np.sum(magnitude[mascara] ** 2)


def contar_picos_relevantes(sinal):
    envoltoria = np.abs(sinal)

    altura_minima = np.mean(envoltoria) + (2 * np.std(envoltoria))
    distancia_minima = 1000

    picos, _ = find_peaks(
        envoltoria,
        height=altura_minima,
        distance=distancia_minima,
    )

    return len(picos)


def gerar_grafico_comparativo_resultados(resultados_df: pd.DataFrame):
    if resultados_df.empty:
        return

    caminho_rms = GRAFICOS_DIR / "comparativo_rms.png"

    plt.figure(figsize=(12, 5))
    plt.bar(resultados_df["condicao"], resultados_df["rms"])
    plt.title("Comparativo de RMS por medição")
    plt.xlabel("Condição")
    plt.ylabel("RMS")
    plt.xticks(rotation=20)
    plt.grid(axis="y")
    plt.tight_layout()
    plt.savefig(caminho_rms, dpi=150)
    plt.close()

    caminho_energia = GRAFICOS_DIR / "comparativo_energia_media.png"

    plt.figure(figsize=(12, 5))
    plt.bar(resultados_df["condicao"], resultados_df["energia_media"])
    plt.title("Comparativo de energia média por medição")
    plt.xlabel("Condição")
    plt.ylabel("Energia média")
    plt.xticks(rotation=20)
    plt.grid(axis="y")
    plt.tight_layout()
    plt.savefig(caminho_energia, dpi=150)
    plt.close()

    caminho_picos = GRAFICOS_DIR / "comparativo_picos.png"

    plt.figure(figsize=(12, 5))
    plt.bar(resultados_df["condicao"], resultados_df["quantidade_picos"])
    plt.title("Comparativo de quantidade de picos por medição")
    plt.xlabel("Condição")
    plt.ylabel("Quantidade de picos")
    plt.xticks(rotation=20)
    plt.grid(axis="y")
    plt.tight_layout()
    plt.savefig(caminho_picos, dpi=150)
    plt.close()


def validar_estrutura():
    if not DADOS_PATH.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {DADOS_PATH}")

    if not AUDIO_DIR.exists():
        raise FileNotFoundError(f"Pasta de áudios não encontrada: {AUDIO_DIR}")


def analisar_medicoes():
    validar_estrutura()

    medicoes_df = pd.read_csv(DADOS_PATH)
    resultados = []

    for _, medicao in medicoes_df.iterrows():
        arquivo = medicao["arquivo"]
        caminho_audio = AUDIO_DIR / arquivo

        if not caminho_audio.exists():
            print(f"Arquivo não encontrado: {caminho_audio}")
            continue

        print(f"Processando: {arquivo}")

        sinal, taxa_amostragem = carregar_audio(caminho_audio)
        sinal_filtrado = aplicar_filtro_passa_faixa(sinal, taxa_amostragem)

        nome_base = Path(arquivo).stem
        titulo_base = f"{medicao['local']} - {medicao['condicao']}"

        gerar_grafico_tempo(
            sinal=sinal,
            taxa_amostragem=taxa_amostragem,
            caminho_saida=GRAFICOS_DIR / f"{nome_base}_tempo.png",
            titulo=f"Forma de onda - {titulo_base}",
        )

        gerar_grafico_fft(
            sinal=sinal,
            taxa_amostragem=taxa_amostragem,
            caminho_saida=GRAFICOS_DIR / f"{nome_base}_fft.png",
            titulo=f"FFT - {titulo_base}",
        )

        gerar_grafico_comparativo_filtro(
            sinal_original=sinal,
            sinal_filtrado=sinal_filtrado,
            taxa_amostragem=taxa_amostragem,
            caminho_saida=GRAFICOS_DIR / f"{nome_base}_filtro.png",
            titulo=f"Comparação original x filtrado - {titulo_base}",
        )

        gerar_espectrograma(
            sinal=sinal,
            taxa_amostragem=taxa_amostragem,
            caminho_saida=GRAFICOS_DIR / f"{nome_base}_espectrograma.png",
            titulo=f"Espectrograma - {titulo_base}",
        )

        metricas = calcular_metricas(sinal, taxa_amostragem)

        resultados.append({
            "id": medicao["id"],
            "arquivo": arquivo,
            "local": medicao["local"],
            "data": medicao["data"],
            "hora": medicao["hora"],
            "duracao_segundos": medicao["duracao_segundos"],
            "condicao": medicao["condicao"],
            "observacao": medicao["observacao"],
            "taxa_amostragem": taxa_amostragem,
            **metricas,
        })

    resultados_df = pd.DataFrame(resultados)

    resultados_df.to_csv(RESULTADOS_PATH, index=False)

    gerar_grafico_comparativo_resultados(resultados_df)

    print("Análise finalizada.")
    print(f"Resultados salvos em: {RESULTADOS_PATH}")
    print(f"Gráficos salvos em: {GRAFICOS_DIR}")


if __name__ == "__main__":
    analisar_medicoes()