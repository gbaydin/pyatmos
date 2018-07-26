# pyatmos

A Docker image for [Atmos](https://github.com/VirtualPlanetaryLaboratory/atmos) and a Python package for interacting with Atmos, for NASA FDL 2018 astrobiology challenges.

Initial work by Adam Cobb and Atilim Gunes Baydin. Further development by William Fawcett. 


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

### Docker on google cloud

Setup the docker image on the google cloud:

    # build the docker image, tag it, and upload to repository 
    gcloud builds submit --tag gcr.io/i-agility-205814/pyatmos .

    # you may need to authenticate, if so, do 
    gcloud auth configure-docker
    gcloud auth login
  




## Auxiliary information

### Seting up docker on google cloud 

To upload your docker image to the google cloud, create your docker file as normal and build it. In this example the docker image will be called quickstart-image:
    
    # build the docker image 
    docker build -t quickstart-image .

    # tag it
    docker tag quickstart-image gcr.io/i-agility-205814/quickstart-image:tag1

Note that here, `i-agility-205814` is the google cloud Project ID [projectid]. tag1 is the name of the tag applied to the docker image. Now push the docker image to the docker container registry:

    docker push gcr.io/i-agility-205814/quickstart-image:tag1

You may need to make sure that you have the right credentials if this fails, see: https://cloud.google.com/container-registry/docs/advanced-authentication 
Since this is a test, you can delete the docker image:

    gcloud container images delete gcr.io/i-agility-205814/quickstart-image:tag1 --force-delete-tags

### Other 

Work in progress. Documentation to follow soon

![screenshot](https://gitlab.com/frontierdevelopmentlab/astrobiology/pyatmos/raw/master/screenshot.png)
[projectid] https://cloud.google.com/resource-manager/docs/creating-managing-projects#identifying_projects 
