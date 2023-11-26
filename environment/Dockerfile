FROM python:3.11-slim

ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && apt-get update \
    && apt-get install -y sudo \
    && echo chmod 0440 /etc/sudoers.d/$USERNAME

EXPOSE 8000
RUN sudo apt update && sudo apt-get install -y git lsof
RUN git config --global --add safe.directory /workspace

COPY src/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

USER $USERNAME