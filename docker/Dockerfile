FROM ubuntu:16.04

RUN apt-get update && apt-get install -y --no-install-recommends \
        gfortran \
        git \
        build-essential \
        ca-certificates &&\
    rm -rf /var/lib/apt/lists/*

RUN mkdir /code/ && cd /code/ && git clone https://github.com/VirtualPlanetaryLaboratory/atmos.git
COPY input_clima.dat /code/atmos/CLIMA/IO/TEMPLATES/ModernEarth/input_clima.dat

COPY atmos_wrapper_init.sh /code/atmos/
COPY atmos_wrapper_iterate.sh /code/atmos/

WORKDIR /code/atmos
