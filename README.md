# CICD-Jenkins-K8S

1) install Docker

2) Prepare Jenkins persistent storage
- sudo mkdir -p /srv/jenkins
- sudo chown 1000:1000 /srv/jenkins

3) Start Jenkins (LTS) in Docker
- # create a dedicated network (optional but recommended)
docker network create ci-net || true
- # Run Jenkins LTS with Java 17
docker run -d --name jenkins \
--restart unless-stopped \
--network ci-net \
-p 8080:8080 -p 50000:50000 \
-v /srv/jenkins:/var/jenkins_home \
jenkins/jenkins:lts-jdk17

- # get the initial admin password and use it to log in to Jenkins UI and configure your username and password (step 4).
docker exec -it jenkins bash -lc 'cat /var/jenkins_home/secrets/initialAdminPassword'

4) In a browser, open "http://VM_public_IP:8080/"
- log in with initial admin password, set up new username and password.
- install your plugins.
- set Jenkins URL to "http://VM_public_IP:8080/"


