FROM quay.tiplab.local/openetra/ubuntu:jammy

# install requirement dependencies
COPY . .
RUN echo 'wireshark-common wireshark-common/install-setuid boolean true' | debconf-set-selections && \
    apt update && \ 
    apt install python3 python3-pip curl git tshark wireshark -y && \
    pip install -r /requirements.txt
ENV TZ=Asia/Bangkok

# kubectl install
RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl && \
    chmod +x ./kubectl && \
    mv ./kubectl /usr/local/bin/kubectl
ENV KUBECONFIG=/kube-config
RUN chmod +x deployment/krew.sh && bash krew.sh
RUN kubectl krew install sniff

#helm install
RUN curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 && \
    chmod +x get_helm.sh && ./get_helm.sh

#running service
EXPOSE 8000
CMD [ "python3", "manage.py", "runserver", "0.0.0.0:8000" ]