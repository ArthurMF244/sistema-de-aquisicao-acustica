# Sistema de Aquisição Acústica

Projeto desenvolvido para análise e processamento de sinais acústicos relacionados a ruídos de escapamentos barulhentos.

O objetivo é organizar áudios em formato WAV, processar os sinais com Python e gerar resultados para análise temporal, análise espectral por FFT, aplicação de filtros digitais e comparação entre as medições.

## Estrutura do projeto

```text
SISTEMA DE AQUISIÇÃO ACÚSTICA/
├── audios/
│   └── wav/
│       ├── AudioC4Arthur.wav
│       ├── DavyCB500.wav
│       ├── SamuelMusica.wav
│       └── SamuelUP.wav
├── dados/
│   └── medicoes.csv
├── graficos/
├── src/
│   ├── 01_base_dados.py
│   ├── 02_analise_temporal.py
│   ├── 03_analise_fft.py
│   ├── 04_processamento_filtro.py
│   ├── 05_comparacao_resultados.py
│   ├── audio_utils.py
│   └── config.py
├── .dockerignore
├── docker-compose.yml
├── Dockerfile
├── README.md
└── requirements.txt
```

## Pré-requisitos

Para executar o projeto, é necessário ter instalado:

* Docker;

Os áudios devem ficar dentro da pasta:

```text
audios/wav/
```

## Arquivo de medições

O arquivo `dados/medicoes.csv` contém a lista dos áudios que serão processados.

Exemplo:

```csv
id,arquivo
1,AudioC4Arthur.wav
2,DavyCB500.wav
3,SamuelMusica.wav
4,SamuelUP.wav
```

O nome dos arquivos no CSV precisa ser exatamente igual ao nome dos arquivos dentro da pasta `audios/wav`.

## Bibliotecas utilizadas

As bibliotecas Python utilizadas no projeto estão no arquivo `requirements.txt`:

```text
numpy
pandas
scipy
matplotlib
```

Essas bibliotecas são usadas para:

* carregar arquivos WAV;
* manipular dados em CSV;
* calcular métricas dos sinais;
* aplicar FFT;
* aplicar filtros digitais;
* gerar gráficos.

## Subindo o ambiente com Docker

Na raiz do projeto, execute:

```bash
docker compose build
```

Esse comando cria a imagem Docker com as dependências necessárias.

Caso seja a primeira execução ou alguma dependência tenha sido alterada no `requirements.txt`, execute novamente:

```bash
docker compose build
```

## Executando as etapas do projeto

As etapas devem ser executadas uma por vez, na ordem abaixo.

### 1. Base de dados acústicos

Essa etapa lê os arquivos WAV e gera uma base com informações técnicas dos áudios, como taxa de amostragem, quantidade de canais, duração e RMS.

Comando:

```bash
docker compose run --rm python-audio python src/01_base_dados.py
```

Saída esperada:

```text
dados/01_base_audios.csv
```

---

### 2. Análise temporal

Essa etapa gera gráficos da amplitude do sinal ao longo do tempo e identifica picos de amplitude.

Comando:

```bash
docker compose run --rm python-audio python src/02_analise_temporal.py
```

Saídas esperadas:

```text
dados/02_metricas_temporais.csv
graficos/02_temporal/
```

---

### 3. Análise espectral por FFT

Essa etapa aplica a Transformada Rápida de Fourier nos áudios para identificar as frequências predominantes.

Comando:

```bash
docker compose run --rm python-audio python src/03_analise_fft.py
```

Saídas esperadas:

```text
dados/03_fft_frequencias_dominantes.csv
graficos/03_fft/
```

---

### 4. Processamento digital com filtro

Essa etapa aplica um filtro passa-faixa nos sinais acústicos e gera uma comparação entre o sinal original e o sinal filtrado.

Comando:

```bash
docker compose run --rm python-audio python src/04_processamento_filtro.py
```

Saídas esperadas:

```text
dados/04_filtros.csv
audios/processado/
graficos/04_filtro/
```

---

### 5. Comparação entre as medições

Essa etapa compara os quatro áudios utilizando métricas como RMS, energia média, frequência dominante e quantidade de picos.

Comando:

```bash
docker compose run --rm python-audio python src/05_comparacao_resultados.py
```

Saídas esperadas:

```text
dados/05_comparacao_resultados.csv
graficos/05_comparacao/
```

## Executando tudo em sequência

Também é possível executar todas as etapas uma após a outra:

```bash
docker compose run --rm python-audio python src/01_base_dados.py
docker compose run --rm python-audio python src/02_analise_temporal.py
docker compose run --rm python-audio python src/03_analise_fft.py
docker compose run --rm python-audio python src/04_processamento_filtro.py
docker compose run --rm python-audio python src/05_comparacao_resultados.py
```

## Verificando containers

Para verificar os containers do projeto:

```bash
docker compose ps
```

Para verificar todos os containers do Docker:

```bash
docker ps -a
```

## Parando o ambiente

Caso algum container fique ativo, use:

```bash
docker compose down
```

## Limpando imagens e cache de build

Caso seja necessário limpar cache de build:

```bash
docker builder prune -f
```

Caso queira remover containers parados:

```bash
docker container prune -f
```

## Observações importantes

Os áudios utilizados neste projeto possuem diferenças técnicas, como duração, taxa de amostragem, quantidade de canais e escala de amplitude. Por isso, os resultados devem ser interpretados como uma análise experimental dos sinais coletados, e não como uma medição acústica oficial calibrada.

Mesmo assim, o projeto permite identificar padrões importantes nos áudios, como:

* presença de picos sonoros;
* predominância de frequências graves;
* diferenças de energia entre os sinais;
* efeito da aplicação de filtros digitais;
* comparação geral entre as medições.

## Objetivo final

O projeto busca demonstrar como técnicas de processamento digital de sinais podem ser aplicadas na análise de ruídos ambientais, especialmente ruídos relacionados a escapamentos barulhentos.

A partir dos gráficos e métricas geradas, é possível compreender melhor o comportamento dos sinais acústicos e utilizar os resultados como apoio para conscientização sobre poluição sonora em ambientes urbanos e comunitários.
