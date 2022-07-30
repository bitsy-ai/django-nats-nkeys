FROM python:3.9-slim-buster

RUN apt-get update \
  # dependencies for building Python packages
  && apt-get install -y build-essential \
  # psycopg2 dependencies
  && apt-get install -y libpq-dev \
  # Translations dependencies
  && apt-get install -y gettext \
  && apt-get install -y postgresql \
  && apt-get -y install wget xvfb xauth poppler-utils \
  # required for ssh-keygen and signing
  && apt-get install -y openssh-server \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

# install nsc command-line tool
RUN wget https://raw.githubusercontent.com/nats-io/nsc/master/install.py -O install-nsc.py
RUN python3 install-nsc.py
RUN rm install-nsc.py
RUN cp $HOME/.nsccli/bin/nsc /usr/local/bin/nsc

RUN mkdir /workspace
WORKDIR /workspace
ADD requirements.txt .
ADD dev-requirements.txt .
ADD Makefile .
RUN python -m pip install --upgrade pip wheel setuptools
RUN PYTHON=$(which python3) make dev-install

ADD docker/entrypoint /entrypoint
RUN echo "/workspace" > /usr/local/lib/python3.9/site-packages/django_nats_nkeys.pth


ENTRYPOINT [ "/entrypoint" ]
