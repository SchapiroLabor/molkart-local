FROM continuumio/miniconda3

# Copy the environment file
COPY environment.yml .

# Install system dependencies
RUN apt-get update -qq && apt-get install -y \
    build-essential \
    ffmpeg \
    libsm6 \
    libxext6

# Create the conda environment
RUN conda env create -f environment.yml

# Set the PATH to use the conda environment
ENV PATH="/opt/conda/envs/molkart_local/bin:$PATH"

# Set the default shell to bash (already the default)
SHELL ["/bin/bash", "-c"]

# Activate the conda environment by default when starting a shell
# This will ensure that the conda environment's python is used
RUN echo "source activate molkart_local" > ~/.bashrc
ENV BASH_ENV ~/.bashrc

# Set the working directory
WORKDIR /local

# Copy the current directory contents into the container at /local
COPY . .
