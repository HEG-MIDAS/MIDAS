FROM ubuntu:jammy

RUN apt-get update

RUN DEBIAN_FRONTEND=noninteractive TZ=Europe/UTC+1 apt-get install -y apache2

RUN apt-get install -y libapache2-mod-shib shibboleth-sp-common shibboleth-sp-utils curl nano

RUN shib-keygen -f -u _shibd -h gexplore.ch -y 10 -o /etc/shibboleth/
# RUN curl --output /etc/shibboleth/shibboleth2.xml 'https://www.switch.ch/aai/docs/shibboleth/SWITCH/3.3/sp/deployment/download/customize.php/shibboleth2.xml?osType=nonwindows&hostname=gexplore.ch&targetURL=https%3A%2F%2Fgexplore.ch%2FShibboleth.sso%2FSession&keyPath=%2Fetc%2Fshibboleth%2Fsp-key.pem&certPath=%2Fetc%2Fshibboleth%2Fsp-cert.pem&federation=SWITCHaai&supportEmail=aai%40gexplore.ch&wayfURL=https%3A%2F%2Fwayf.switch.ch%2FSWITCHaai%2FWAYF&metadataURL=http%3A%2F%2Fmetadata.aai.switch.ch%2Fentities%2Feduid&metadataFile=metadata.eduid.ch.xml&eduIDEntityID=https%3A%2F%2Feduid.ch%2Fidp%2Fshibboleth&hide=windows-only,metadataattributespart1,metadataattributespart2,interfederation,'
RUN curl --output /etc/shibboleth/attribute-map.xml 'https://www.switch.ch/aai/docs/shibboleth/SWITCH/3.3/sp/deployment/download/customize.php/attribute-map.xml?osType=nonwindows&hide='
#RUN curl --output /etc/shibboleth/attribute-policy.xml 'https://www.switch.ch/aai/docs/shibboleth/SWITCH/3.3/sp/deployment/download/customize.php/attribute-policy.xml?osType=nonwindows&hide='

RUN curl --output /etc/shibboleth/SWITCHaaiRootCA.crt.pem http://ca.aai.switch.ch/SWITCHaaiRootCA.crt.pem

RUN service shibd start

COPY 000-default.conf /etc/apache2/sites-enabled/000-default.conf
COPY shibboleth2.xml /etc/shibboleth/shibboleth2.xml
COPY attribute-policy.xml /etc/shibboleth/attribute-policy.xml

EXPOSE 80
CMD apachectl -D FOREGROUND
