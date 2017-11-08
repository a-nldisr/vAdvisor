FROM fedora:26

MAINTAINER "Roman Mohr" <rmohr@redhat.com>

ENV VERSION master

EXPOSE 8181

RUN dnf -y install tar libvirt-python3 && \
    dnf -y install python3-greenlet && \
    dnf clean all && \
    pip3 --no-cache-dir install gevent && \
    rm -rf ~/.pip

LABEL io.cadvisor.metric.prometheus-vadvisor="/var/vadvisor/cadvisor_config.json"

RUN \
    curl -LO https://github.com/kubevirt/vAdvisor/archive/$VERSION.tar.gz#/vAdvisor-$VERSION.tar.gz && \
    tar xf vAdvisor-$VERSION.tar.gz && \
    cd vAdvisor-$VERSION && \
    sed -i '/libvirt-python/d' requirements.txt && \
    dnf install -y gcc redhat-rpm-config python3-devel && \
    pip3 --no-cache-dir install -r requirements.txt && \
    pip3 --no-cache-dir install . && \
    mkdir -p /var/vadvisor && \
    cp docker/cadvisor_config.json /var/vadvisor/ && \
    cp docker/entrypoint.sh / && \
    rm -rf ~/.pip && \
    cd .. && \
    rm -rf vAdvisor-$VERSION* && \
    dnf clean all

ENTRYPOINT [ "/bin/bash", "/entrypoint.sh" ]
