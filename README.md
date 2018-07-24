# pyatmos

A Docker image for [Atmos](https://github.com/VirtualPlanetaryLaboratory/atmos) and a Python package for interacting with Atmos, for NASA FDL 2018 astrobiology challenges.

Initial work by Adam Cobb and Atilim Gunes Baydin.

Work in progress. Documentation to follow soon.

![screenshot](https://gitlab.com/frontierdevelopmentlab/astrobiology/pyatmos/raw/master/screenshot.png)

## How to install

You can clone this repository and install the `pyatmos` package. You need to have Docker installed in your system.

The Python package pulls the latest Docker image for atmos from the FDL GitLab registry, here: https://gitlab.com/frontierdevelopmentlab/astrobiology/pyatmos/container_registry



### Prerequisites
Make sure python and pip are installed:

    sudo apt update
    sudo apt install python python-dev python3 python3-dev
    wget https://bootstrap.pypa.io/get-pip.py
    sudo python get-pip.py


Make sure docker is installed:
    
    # install docker, either install [Docker CE](https://www.docker.com/community-edition) for your system
    # or, from the command line:  
    sudo apt install docker.io

    # You may need to add yourself to the "docker group" so you have the correct permissions 
    sudo usermod -a -G docker $USER 

    # Test that you can access docker (you may need to restart the machine first if this does not work)
    docker run hello-world

### Install the package

```
git clone git@gitlab.com:frontierdevelopmentlab/astrobiology/pyatmos.git
cd pyatmos
pip install -e .
```
