FROM ubuntu:16.04
MAINTAINER willfaw@gmail.com

RUN apt-get update && apt-get install -y --no-install-recommends \
        gfortran \
        git \
        build-essential \
        ca-certificates &&\
    rm -rf /var/lib/apt/lists/*


RUN mkdir /code/ && cd /code/ && git clone https://gitlab.com/frontierdevelopmentlab/astrobiology/atmos.git

RUN cp /code/atmos/PHOTOCHEM/INPUTFILES/TEMPLATES/ModernEarth/in.dist  /code/atmos/PHOTOCHEM/in.dist

RUN cp /code/atmos/PHOTOCHEM/INPUTFILES/TEMPLATES/ModernEarth/input_photchem.dat /code/atmos/PHOTOCHEM/INPUTFILES/; cp /code/atmos/PHOTOCHEM/INPUTFILES/TEMPLATES/ModernEarth/reactions.rx /code/atmos/PHOTOCHEM/INPUTFILES/; cp /code/atmos/PHOTOCHEM/INPUTFILES/TEMPLATES/ModernEarth/parameters.inc /code/atmos/PHOTOCHEM/INPUTFILES/; cp /code/atmos/PHOTOCHEM/INPUTFILES/TEMPLATES/ModernEarth/species.dat /code/atmos/PHOTOCHEM/INPUTFILES/

RUN echo species.dat
RUN cat /code/atmos/PHOTOCHEM/INPUTFILES/species.dat
RUN cp /code/atmos/PHOTOCHEM/INPUTFILES/TEMPLATES/ModernEarth/PLANET.dat /code/atmos/PHOTOCHEM/INPUTFILES/

RUN cd /code/atmos && make -f PhotoMake

RUN cd /code/atmos && ./Photo.run

RUN cp /code/atmos/CLIMA/IO/TEMPLATES/ModernEarth/input_clima.dat  /code/atmos/CLIMA/IO 

RUN cd /code/atmos && make -f ClimaMake

RUN cd /code/atmos && ./Clima.run

