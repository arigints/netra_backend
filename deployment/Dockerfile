FROM quay.tiplab.local/openetra/ubuntu:jammy

LABEL maintainer="gintingari73@gmail.com"

# set and install requirement packages
COPY . /app
WORKDIR /app
ENV TZ=Asia/Bangkok
RUN echo 'wireshark-common wireshark-common/install-setuid boolean true' | debconf-set-selections && \
    apt update && \
    apt install python3 python3-pip curl wget unzip make git tshark wireshark -y && \
    pip install -r /app/requirements.txt

# kubectl, krew, and ksniff install
RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl && \
    chmod +x ./kubectl && \
    mv ./kubectl /usr/local/bin/kubectl && \ 
    chmod +x /app/deployment/ksniff.sh && bash /app/deployment/ksniff.sh
ENV KUBECONFIG=/app/deployment/kube-config

#helm install
RUN curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 && \
    chmod +x get_helm.sh && ./get_helm.sh

#running service
EXPOSE 8000
CMD [ "python3", "manage.py", "runserver", "0.0.0.0:8000" ]