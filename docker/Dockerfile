FROM ubuntu:16.04
MAINTAINER Will Fawcett <willfaw@gmail.com>

# Get OS 
RUN apt-get update && apt-get install -y --no-install-recommends \
        gfortran \
        git \
        build-essential \
        ca-certificates &&\
    rm -rf /var/lib/apt/lists/*

# dummy command for docker 
RUN echo hello world 2

# Get ATMOS
RUN mkdir /code/ && cd /code/ && git clone https://gitlab.com/frontierdevelopmentlab/astrobiology/atmos.git
RUN export ATMOSDIR=/code/atmos 

# Sort out AMTOS files 
RUN cp /code/atmos/PHOTOCHEM/INPUTFILES/TEMPLATES/ModernEarth/in.dist  /code/atmos/PHOTOCHEM/in.dist; cp /code/atmos/PHOTOCHEM/INPUTFILES/TEMPLATES/ModernEarth/input_photchem.dat /code/atmos/PHOTOCHEM/INPUTFILES/; cp /code/atmos/PHOTOCHEM/INPUTFILES/TEMPLATES/ModernEarth/reactions.rx /code/atmos/PHOTOCHEM/INPUTFILES/; cp /code/atmos/PHOTOCHEM/INPUTFILES/TEMPLATES/ModernEarth/parameters.inc /code/atmos/PHOTOCHEM/INPUTFILES/; cp /code/atmos/PHOTOCHEM/INPUTFILES/TEMPLATES/ModernEarth/species.dat /code/atmos/PHOTOCHEM/INPUTFILES/; cp /code/atmos/PHOTOCHEM/INPUTFILES/TEMPLATES/ModernEarth/PLANET.dat /code/atmos/PHOTOCHEM/INPUTFILES/; cp /code/atmos/CLIMA/IO/TEMPLATES/ModernEarth/input_clima.dat  /code/atmos/CLIMA/IO 

# Check correct species file 
RUN echo species.dat; cat /code/atmos/PHOTOCHEM/INPUTFILES/species.dat

# Compile and run photo
RUN cd /code/atmos && make -f PhotoMake && ./Photo.run

# Compile and run clima 
RUN cd /code/atmos && make -f ClimaMake && ./Clima.run

# Make sure we're in the root directory 
RUN cd / 
