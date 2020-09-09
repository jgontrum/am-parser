# Provide the Java runtime
FROM adoptopenjdk/openjdk8:ubuntu

# Install Python 3.7
RUN apt-get update && apt-get remove -y python3.6 && \
    apt install -y git software-properties-common build-essential && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt-get install -y python3.7 python3.7-dev

# Install Pip
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3.7 get-pip.py && rm get-pip.py && \
    ln -s /usr/bin/python3.7 /usr/bin/python

# Install all required Python packages
RUN pip --no-cache-dir install cython scikit-learn==0.22.2 && \
    pip --no-cache-dir install torch==1.2.0+cpu torchvision==0.4.0+cpu -f https://download.pytorch.org/whl/torch_stable.html && \
    pip --no-cache-dir install allennlp==0.8.4 git+https://github.com/andersjo/dependency_decoding jnius

# Download and include spaCy models
RUN python -m spacy download en_core_web_md

# Install FastAPI
RUN pip install --no-cache-dir fastapi pydantic uvicorn gunicorn

RUN git clone https://github.com/tiangolo/uvicorn-gunicorn-docker.git && \
    cd uvicorn-gunicorn-docker && git checkout 39534cb && \
    cp docker-images/start.sh /start.sh && \
    chmod +x /start.sh && \
    cp docker-images/gunicorn_conf.py /gunicorn_conf.py && \
    cp docker-images/start-reload.sh /start-reload.sh && \
    chmod +x /start-reload.sh && \
    cd .. && rm -rf uvicorn-gunicorn-docker

COPY . /app
WORKDIR /app/

ENV PYTHONPATH=/app
ENV MAX_WORKERS=1
ENV WEB_CONCURRENCY=1
ENV TIMEOUT=500
ENV GRACEFUL_TIMEOUT=500

EXPOSE 80

# Run the start script, it will check for an /app/prestart.sh script (e.g. for migrations)
# And then will start Gunicorn with Uvicorn
CMD ["/start.sh"]
