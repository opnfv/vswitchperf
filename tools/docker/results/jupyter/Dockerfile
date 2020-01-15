FROM jupyter/scipy-notebook

RUN python --version

RUN conda install --quiet --yes -c \
    conda-forge osmnx dask

RUN pip install -U graphviz paramiko

RUN echo "c.NotebookApp.token=''" >> $HOME/.jupyter/jupyter_notebook_config.py 

VOLUME /notebooks
VOLUME /data

RUN mkdir /data/results
WORKDIR /notebooks
