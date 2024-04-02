FROM quay.tiplab.local/openetra/python:3

ENV PYTHONUNBUFFERED 1

COPY requirements.txt .

RUN pip install -r requirements.txt

ENV TZ=Asia/Bangkok

RUN django-admin startproject netra_backend

COPY . /netra_backend

WORKDIR /netra_backend

ENV KUBECONFIG=/netra_backend/kube-config

EXPOSE 8000

CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]
