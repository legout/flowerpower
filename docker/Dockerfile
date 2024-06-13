FROM quay.io/jupyter/base-notebook

ARG CODE_VERSION=4.89.1
ARG PLATFORM=arm64

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

USER root

# Install all OS dependencies for a fully functional Server
RUN apt-get update --yes && \
    apt-get install --yes --no-install-recommends \
    # Common useful utilities
    curl \
    git \
    nano-tiny \
    tzdata \
    unzip \
    # git-over-ssh
    openssh-client \
    # Enable clipboard on Linux host systems
    xclip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Create alternative for nano -> nano-tiny
RUN update-alternatives --install /usr/bin/nano nano /bin/nano-tiny 10

# Install code-server

RUN curl -fOL https://github.com/coder/code-server/releases/download/v$CODE_VERSION/code-server_${CODE_VERSION}_${PLATFORM}.deb \
    && dpkg -i code-server_${CODE_VERSION}_${PLATFORM}.deb \
    && rm -f code-server_${CODE_VERSION}_${PLATFORM}.deb

# Switch back to jovyan to avoid accidental container runs as root
USER ${NB_UID}

#conda install jupyterlab -y && \
RUN conda install jupyter-server-proxy jupyter-vscode-proxy  -y && \
    conda clean --tarballs --index-cache --packages --yes && \
    find ${CONDA_DIR} -follow -type f -name '*.a' -delete && \
    find ${CONDA_DIR} -follow -type f -name '*.pyc' -delete && \
    conda clean --force-pkgs-dirs --all --yes
#  && \
#sudo echo ". ${CONDA_DIR}/etc/profile.d/conda.sh && conda activate base" >> /etc/skel/.bashrc && \
#echo ". ${CONDA_DIR}/etc/profile.d/conda.sh && conda activate base" >> ~/.bashrc

COPY assets/GitHub.copilot-1.199.0.vsix GitHub.copilot-1.199.0.vsix
COPY assets/GitHub.copilot-chat-0.15.2024043005.vsix GitHub.copilot-chat-0.15.2024043005.vsix

RUN code-server --install-extension ms-toolsai.jupyter && \
    code-server --install-extension ms-python.python && \
    code-server --install-extension mtxr.sqltools && \
    code-server --install-extension bungcip.better-toml && \
    code-server --install-extension ms-python.black-formatter && \
    code-server --install-extension ms-python.isort && \
    code-server --install-extension redhat.vscode-yaml && \
    code-server --install-extension charliermarsh.ruff && \
    code-server --install-extension esbenp.prettier-vscode && \
    code-server --install-extension mtxr.sqltools-driver-sqlite && \
    code-server --install-extension mtxr.sqltools-driver-pg && \
    code-server --install-extension GitHub.copilot-1.199.0.vsix && \
    code-server --install-extension GitHub.copilot-chat-0.15.2024043005.vsix && \
    rm -r GitHub.copilot-*.vsix && \
    rm -r /home/jovyan/.local/share/code-server/CachedExtensionVSIXs/


#EXPOSE 8888
#EXPOSE 3000
#ENTRYPOINT  ["jupyter", "lab", "--ip=0.0.0.0", "--allow-root", "--no-browser", "--NotebookApp.token=''"]