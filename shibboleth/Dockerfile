FROM ubuntu:jammy
ENV TZ="Europe/Zurich"
RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y apache2
RUN apt-get install -y libapache2-mod-shib shibboleth-sp-common shibboleth-sp-utils curl nano

RUN shib-keygen -f -u _shibd -h gexplore.ch -y 10 -o /etc/shibboleth/
RUN curl --output /etc/shibboleth/attribute-map.xml 'https://www.switch.ch/aai/docs/shibboleth/SWITCH/3.3/sp/deployment/download/customize.php/attribute-map.xml?osType=nonwindows&hide='
RUN curl --output /etc/shibboleth/SWITCHaaiRootCA.crt.pem http://ca.aai.switch.ch/SWITCHaaiRootCA.crt.pem

RUN service shibd start

COPY 000-default.conf /etc/apache2/sites-enabled/000-default.conf
COPY shibboleth2.xml /etc/shibboleth/shibboleth2.xml
COPY attribute-policy.xml /etc/shibboleth/attribute-policy.xml

EXPOSE 80
CMD apachectl -D FOREGROUND
