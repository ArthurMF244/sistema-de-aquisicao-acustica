from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

AUDIO_DIR = BASE_DIR / "audios" / "wav"
DADOS_DIR = BASE_DIR / "dados"
GRAFICOS_DIR = BASE_DIR / "graficos"
AUDIO_PROCESSADO_DIR = BASE_DIR / "audios" / "processado"

MEDICOES_PATH = DADOS_DIR / "medicoes.csv"

BASE_AUDIOS_PATH = DADOS_DIR / "01_base_audios.csv"
METRICAS_TEMPORAIS_PATH = DADOS_DIR / "02_metricas_temporais.csv"
FFT_RESULTADOS_PATH = DADOS_DIR / "03_fft_frequencias_dominantes.csv"
FILTRO_RESULTADOS_PATH = DADOS_DIR / "04_filtros.csv"
COMPARACAO_RESULTADOS_PATH = DADOS_DIR / "05_comparacao_resultados.csv"


def preparar_pastas():
    DADOS_DIR.mkdir(parents=True, exist_ok=True)
    GRAFICOS_DIR.mkdir(parents=True, exist_ok=True)
    AUDIO_PROCESSADO_DIR.mkdir(parents=True, exist_ok=True)
