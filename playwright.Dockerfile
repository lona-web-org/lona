FROM mcr.microsoft.com/playwright:v1.34.0-jammy

# upgrade ubuntu
RUN apt update && apt upgrade -y

# setup tzdata (required by pyenv dependencies)
RUN apt update && DEBIAN_FRONTEND=noninteractive TZ=Gmt/UTC apt-get -y install tzdata

# install pyenv dependencies
RUN apt update && apt install -y \
	git build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev \
	libsqlite3-dev curl libncursesw5-dev xz-utils tk-dev libxml2-dev \
	libxmlsec1-dev libffi-dev liblzma-dev

# setup pyenv
RUN git clone https://github.com/yyuu/pyenv.git .pyenv
ENV PYENV_ROOT $HOME/.pyenv
ENV PATH $PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH

RUN pyenv install 3.7:latest
RUN pyenv install 3.8:latest
RUN pyenv install 3.9:latest
RUN pyenv install 3.10:latest
RUN pyenv install 3.11:latest

RUN pyenv global `pyenv versions --bare`

# setup commandline tools
RUN pip3.10 install --upgrade pip tox
RUN pyenv rehash
