FROM jupyter/scipy-notebook

RUN python --version

RUN conda install --quiet --yes -c \
    conda-forge osmnx dask

RUN pip install -U graphviz paramiko

VOLUME /notebooks
WORKDIR /notebooks
