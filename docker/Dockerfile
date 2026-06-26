FROM ubuntu:26.04

ARG DEBIAN_FRONTEND=noninteractive
ARG SYFT_VERSION=1.44.0

RUN apt-get update && apt-get install -y --no-install-recommends \
    autoconf \
    automake \
    binutils \
    bison \
    build-essential \
    ca-certificates \
    cmake \
    curl \
    file \
    flex \
    gettext \
    git \
    jq \
    libcurl4-openssl-dev \
    libevent-dev \
    liblz4-dev \
    liblzma-dev \
    libncurses-dev \
    libpcre2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libssl-dev \
    libtool \
    libzstd-dev \
    make \
    ninja-build \
    perl \
    pkg-config \
    postgresql-server-dev-all \
    python3 \
    unzip \
    wget \
    xz-utils \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh \
    | sh -s -- -b /usr/local/bin "v${SYFT_VERSION}"

WORKDIR /work

CMD ["/bin/bash"]
