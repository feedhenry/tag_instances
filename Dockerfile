FROM centos:centos7

RUN yum -y --enablerepo=extras install epel-release
RUN yum -y install python-pip

RUN pip install boto==2.46.1

ADD . .

ENTRYPOINT ["python", "instances.py"]