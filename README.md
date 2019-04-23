# Install

```
git clone https://github.com/anylatex/backend.git
```

# Run

## Run with Docker

Install docker and docker-compose first. Then run with following commands.

Check into the `dockerfiles` and rename `example-config-docker.json`.

```
cd dockerfiles
mv example-config-docker.json config.json
```

Pull texlive-2018 docker image.

```
sudo docker pull gyhh/texlive:latest
```

Build docker images and run.

```
sudo docker-compose build
sudo docker-compose up

```

Now, the application runs on `http://127.0.0.1:4000`.


## Run without Docker

Install MongoDB and texlive-2018 with full scheme first.


Install requirments and rename `example-config.json`.

```
pip3 install requirments.txt
mv example-config.json config.json
```

Run api:

```
python3 -m api.api
```

or

```
gunicorn -w 4 -b 127.0.0.1:4000 api.api:app
```

Run compiling service:

```
python3 -m compiler.compiler
```

