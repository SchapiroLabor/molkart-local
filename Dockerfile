FROM continuumio/miniconda3

COPY environment.yml .
RUN apt-get update -qq && apt-get install -y \
    build-essential \
    ffmpeg \
    libsm6 \
    libxext6

RUN conda env create -f environment.yml
ENV PATH="/opt/conda/envs/molkart_local/bin:$PATH"
WORKDIR /local
COPY . .