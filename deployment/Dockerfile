FROM ubuntu:jammy

LABEL maintainer="gintingari73@gmail.com"

# set and install requirement packages
COPY . /app
WORKDIR /install
ENV TZ=Asia/Bangkok
ENV KUBECONFIG=/app/deployment/kube-config
RUN echo 'wireshark-common wireshark-common/install-setuid boolean true' | debconf-set-selections && \
    apt-get update && apt-get install -y python3 python3-pip curl wget unzip make git tshark wireshark && \
    pip install --no-cache-dir -r /app/requirements.txt && \
    curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl && \
    chmod +x ./kubectl && chmod go-r $KUBECONFIG && \
    mv ./kubectl /usr/local/bin/kubectl && \
    chmod +x /app/deployment/ksniff.sh && bash /app/deployment/ksniff.sh && \
    curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 && \
    chmod +x get_helm.sh && ./get_helm.sh && \
    rm -rf /install && rm -rf /var/lib/apt/lists/*
WORKDIR /app

#running service
EXPOSE 8000
CMD [ "python3", "manage.py", "runserver", "0.0.0.0:8000" ]