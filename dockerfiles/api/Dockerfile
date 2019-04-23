FROM python:3.6-slim

# install git
RUN apt-get update && apt-get install -y git gunicorn \
    && apt-get clean

# clone anylatex api repository and install dependencies
RUN git clone https://github.com/anylatex/backend.git /backend \
    && pip install -r /backend/requirments.txt
WORKDIR /backend

# start
ENTRYPOINT gunicorn -w $((2 * $(grep -c ^processor /proc/cpuinfo) + 1)) -b 0.0.0.0:4000 --access-logfile - api.api:app
