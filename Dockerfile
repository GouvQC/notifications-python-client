FROM debian:buster

ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --only-upgrade libc-bin && \
    apt-get clean && rm -rf /var/lib/apt/lists/*


RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      awscli \
      gcc \
      git \
      gnupg \
      curl \
      ca-certificates \
      jq \
      # pyenv dependencies (https://github.com/pyenv/pyenv/wiki#suggested-build-environment)
      make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev \
      libsqlite3-dev wget curl llvm libncurses5-dev xz-utils tk-dev \
      libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/pyenv/pyenv.git /root/.pyenv

ENV PYENV_ROOT=/root/.pyenv
ENV PATH="$PYENV_ROOT/bin:$PYENV_ROOT/shims:$PATH"

RUN ls /root/.pyenv/bin
RUN eval "$(/root/.pyenv/bin/pyenv init - )"

WORKDIR /var/project

COPY tox-python-versions .

RUN xargs -a tox-python-versions -n 1 -P $(nproc) pyenv install

COPY . .

# Make pyenv activate all installed Python versions for tox (available as pythonX.Y)
# The first version in the file will be the one used when running "python"
RUN pyenv global $(tr '\n' ' ' < tox-python-versions)

# Mise � jour de setuptools dans chaque version Python
RUN for v in $(cat tox-python-versions); do \
    /root/.pyenv/versions/$v/bin/pip install --upgrade setuptools==78.1.1; \
  done

RUN make bootstrap

RUN pip install tox
