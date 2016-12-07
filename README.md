# signalserver

SignalServer is intended to become a web app to accompany [QCTools](https://github.com/bavc/qctools). Some early planning documentation is available in this [Vision doc](https://docs.google.com/document/d/1zXtVf47LVEYJvc9nPbLY-0pTDouyyNlsbeFu1YdmMlI/edit?usp=sharing).

## Installation

### From git

```
git checkout git@github.com:bavc/signalserver.git
cd signalserver
FILES_VOLUME_PATH=/files ./quickstart.sh
```


### Dependency

Signalserver can run anywhere as long as the host OS has docker-engine and docker compose are installed. Signalsever is designed using docker in mind. So please install docker-engine and docker-compose before you start. If you are using mac or windows, you can also install docker made for either Window or Mac. You can refer to following documentations for docker installation.

Linux: https://docs.docker.com/engine/installation/

OSX: https://docs.docker.com/engine/installation/mac/#/docker-for-mac

Windows: https://docs.docker.com/engine/installation/windows/


Once you are installed docker engine, docker compose also need to be installed.
Docker-compose needs to be above version 1.7. So if you have an older version of docker-engine or
docker-compose, it probably need to be updated for both. Docker compose instruction for install is below.

https://docs.docker.com/compose/install/

!!! Please follow docker's documentation for these installation exactly according to your OS. !!!

### Environment variable

Singal server has a capacity to accept large number of files. Thus, we also want to give a user to determine where the files are stored in your host OS.

For example, the host OS has 8G of the storage but you mounted extra spece in /data directly of your host OS.  And you want to designate your file storage would be in your /data directly. In this case, your file storage path is :

```
FILES_VOLUME_PATH=/data
```

You can set this value either in the .env file or you can run with ./quickstart script. Default value for this value is:

```
FILES_VOLUME_PATH=/files
```

If you don't have any special arrangement for space, you can just create the .env file with above line in the project root directly. In docker container, it will be stored in /var/signalserver/files directly.

### Running the application

When you have docker-engine and docker-compose is installed and .env file is created with above value, you just need to run below script.

```
./quickstart.sh
```

Then, it should tell you where the IP address of the web server docker container is running.

If you didn't set up the .env file, but you still want to store the files at the specific location,
you can also run the command following way.

```
FILES_VOLUME_PATH=/data ./quickstart.sh
```


### API usage

Once you are running the signalserver and you create your credential at the site, you can upload the file not only from the site, but also using the API from signalserver. The curl command is as below.

```
curl -i -u "username:password" [signalserver IP]:8000/fileuploads/upload/ --upload-file [your file name]
```

Example:
You want to upload the filename '5A_born_digital_ffv1.qctools.xml.gz' to the server 192.168.99.100
and your username and password is user1 and password2

```
curl -i -u "user1:password2" 192.168.99.100:8000/fileuploads/upload/ --upload-file 5A_born_digital_ffv1.qctools.xml.gz
```