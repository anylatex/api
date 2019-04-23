FROM gyhh/texlive:latest

# install dependencies
RUN apt-get update && apt-get install -y git python3.6 python3-pip \
    && apt-get clean

# clone anylatex api repository and install dependencies
RUN git clone https://github.com/anylatex/api.git /api \
    && pip3 install -r /api/requirments.txt
WORKDIR /api

# start
CMD python3.6 -m compiler.compiler
