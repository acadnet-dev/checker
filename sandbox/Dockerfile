FROM gcc:13

# Install dependencies
RUN apt update
RUN apt install libssl-dev

# Install pyenv
RUN curl https://pyenv.run | bash

ENV HOME  /root
ENV PYENV_ROOT $HOME/.pyenv
ENV PATH $PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH

# Install Python 3.11.3
RUN pyenv install 3.11.3
RUN pyenv global 3.11.3
RUN pyenv rehash

# cache requirements
COPY requirements.txt /usr/src/myapp/requirements.txt
WORKDIR /usr/src/myapp
RUN pip install -r requirements.txt

COPY . /usr/src/myapp

CMD ["python", "sandbox.py"]
