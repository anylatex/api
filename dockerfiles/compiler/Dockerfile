FROM python:3.6-slim

# install dependencies
RUN apt-get update && apt-get install -y git \
    && apt-get clean

# clone anylatex api repository and install dependencies
RUN git clone https://github.com/anylatex/backend.git /backend \
    && pip install -r /backend/requirments-docker.txt
WORKDIR /backend

# start
CMD python -m compiler.docker_compiler
