FROM quay.tiplab.local/openetra/ubuntu:jammy

# install requirement dependencies
RUN apt update
RUN apt install python3 python3-pip curl -y
COPY requirements.txt .
RUN pip install -r requirements.txt
ENV TZ=Asia/Bangkok
COPY . .

# kubectl install
RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl
RUN chmod +x ./kubectl
RUN mv ./kubectl /usr/local/bin/kubectl
ENV KUBECONFIG=/kube-config

#helm install
RUN curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3
RUN chmod +x get_helm.sh && ./get_helm.sh

#running service
EXPOSE 8000
CMD [ "python3", "manage.py", "runserver", "0.0.0.0:8000" ]
