FROM quay.tiplab.local/openetra/ubuntu:jammy

# install requirement dependencies
COPY requirements.txt .
RUN apt update && \
    apt install python3 python3-pip curl -y && \
    pip install -r requirements.txt
ENV TZ=Asia/Bangkok
COPY . .

# install kubectl
RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl && \
    chmod +x ./kubectl && \
    mv ./kubectl /usr/local/bin/kubectl
ENV KUBECONFIG=/kube-config

# install kubectl
RUN curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 && \
    chmod +x get_helm.sh && ./get_helm.sh

#running service
EXPOSE 8000
CMD [ "python3", "manage.py", "runserver", "0.0.0.0:8000" ]
