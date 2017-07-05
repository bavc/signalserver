# SignalServer

SignalServer is a web app to accompany [QCTools](https://github.com/bavc/qctools). Some early planning documentation is available in this [Vision doc](https://docs.google.com/document/d/1zXtVf47LVEYJvc9nPbLY-0pTDouyyNlsbeFu1YdmMlI/edit?usp=sharing).

## Installation

### Docker

SignalServer is designed using Docker in mind. Please install BOTH `docker-engine` and `docker-compose` before you start. Downloads of Docker for various OS are available at:

Linux: https://docs.docker.com/engine/installation/

OSX: https://docs.docker.com/engine/installation/mac/#/docker-for-mac

Windows: https://docs.docker.com/engine/installation/windows/

SignalServer requires `docker-compose` above version 1.7, please update if needed.

https://docs.docker.com/compose/install/

Once you have `docker-engine` and `docker-compose` installed and confirmed Docker is running, you can install SignalServer.

#### For Mac Users

If you installed Docker by using Docker for Mac... there is one more step:

Create a directory where you want to mount the file volume for SignalServer. (default is `/files`)
So create the `/files` directory if you don't have a strong preference about it.

```
mkdir /files
```

Also make sure you give the `/files` directory full permissions. It may give an error if you don't give full permissions.

Then you click on the Docker icon on the top right bar and select "preferences" then select the "File Sharing" tab.

![screen shot 2017-02-09 at 12 49 30 am](https://cloud.githubusercontent.com/assets/720709/22776921/6bd7e742-ee66-11e6-8eb9-e5072a4bb62e.png)

In the File Sharing tab, click '+' icon and select `/files` (the directory you created in previous step). And `/files` should be added to "File Sharing".

![screen shot 2017-02-09 at 12 49 54 am](https://cloud.githubusercontent.com/assets/720709/22776939/80c84282-ee66-11e6-9f6a-6d128af6ca06.png)

#### For Older Docker Environments

If you are running an older Mac or Windows environment with Docker Toolbox, you will need to uncomment the first 4 lines of quickstart.sh or quickstartdev.sh :

```
 #docker-machine create --driver virtualbox default
 #docker-machine start default
 #docker-machine env default
 #eval "$(docker-machine env default)"
```

#### Non-Docker for Mac users, Windows users

If you are using an older version of Mac or Windows, you still need these above four lines, so please uncomment these before you run the quickstart.

#### Docker Troubleshooting

If you run this script often, or if the script gets stuck and doesn't produce any output, you may want to remove the intermediate containers/images every once in a while.

```
docker ps -a -q | xargs docker rm -f
docker images -a -q | xargs docker rmi -f
```

Now SignalServer is ready to be installed.

## Installing SignalServer

### From git

```
git clone https://github.com/bavc/signalserver.git
cd signalserver
./quickstart.sh
```

### Environment variable

SignalServer has a capacity to accept large numbers of files. Thus, we provide an option to determine where the files are stored in your host OS.

For example, the host OS has only 8G of local storage but you mounted extra space in the `/data` directory of your host OS. Then you could designate your file storage to be within the `/data` directory. In this case, your file storage path is:

```
FILES_VOLUME_PATH=/data
```

You can set this value either in the `.env` file or you can run with `./quickstart.sh` script. Default value for this value is:

```
FILES_VOLUME_PATH=/files
```

If you don't have any special arrangement for space, you can just edit the `.env` file with above line in the project root directory. Within the Docker container, it will be stored in the `/var/signalserver/files` directory.

## Running SignalServer

### Quickstart

When you have `docker-engine` and `docker-compose` installed and the `.env` file is created with above value, you just need to run the script below.

```
./quickstart.sh
```

Then, it should tell you where the IP address of the web server Docker container is running.

If you didn't set up the `.env` file, but you still want to store the files at the specific location, you can also run the command following way:

```
FILES_VOLUME_PATH=/data ./quickstart.sh
```

### Frontend

At this point, your application is running on the port of the localhost that `quickstart.sh` tells you.
However, you may not have frontend assets loaded.

If that is the case, open the `frontend.sh` file and change the 1st line as below. In this example,
this person's SignalServer folder is located on `/Users/username/signalserver/Dockerfile-frontend`
So the first line of the frontend.sh should be changed to:

```
docker build -t signalserver-frontend -f /Users/username/signalserver/Dockerfile-frontend .
```

(Note the trailing `.`, which is important).

Once you have changed your `frontend.sh` to your project's Dockerfile-frontend path, save the file and run `frontend.sh`.
After you run `frontend.sh`, run `quickstart.sh` again, following the first step.

```
./frontend.sh
./quickstart.sh
```

And that should be it!

### Cleanup

When doing a lot of development work and building many dockers, you may want to clean up by running `docker ps -a -q | xargs docker rm -f` and `docker images -a -q | xargs docker rmi -f`


# API usage

### Fileupload

Once you are running the SignalServer and you have created your credentials at the site, you can upload the file not only from the site, but also using the SignalServer API. The curl command is:

```
curl -i -u "username:password" [signalserver IP]:8000/fileuploads/upload/ --upload-file [your file name]
```
Example:
You want to upload the filename '5A_born_digital_ffv1.qctools.xml.gz' to the server 192.168.99.100
and your username and password is user1 and password2

```
curl -i -u "user1:password2" 192.168.99.100:8000/fileuploads/upload/ --upload-file 5A_born_digital_ffv1.qctools.xml.gz
```

### Check file existence

The file existence check returns true or false by a given filename.

```
curl -i -u "username:password" [signalserver IP]:8000/fileuploads/check_exist/[your file name]
```
Example:
You want to check the filename '5A_born_digital_ffv1.qctools.xml.gz' exist in the server or not. The server is 192.168.99.100
and your username and password is user1 and password2

```
curl -i -u "user1:password2" 192.168.99.100:8000/fileuploads/check_exist/5A_born_digital_ffv1.qctools.xml.gz
```

### Delete a file from the server

To delete a file by given filename:

```
curl -i -u "username:password" [signalserver IP]:8000/fileuploads/delete_file/ --data "filename=[yourfilename]"
```
Example:
You want to delete the filename '5A_born_digital_ffv1.qctools.xml.gz' from the server. The server is 192.168.99.100
and your username and password is user1 and password2

```
curl -i -u "user1:password2" 192.168.99.100:8000/fileuploads/delete_file/ --data="filename=5A_born_digital_ffv1.qctools.xml.gz"
```

### Create a new group

Create Group allows you to create a new group. The name needs to be unique.
(It will return error message if it is not.)

```
curl -u "username:password" [signalserver IP]:8000/groups/create_group -data="groupname=[your groupname]"
```
Example:
You want to create a new group named 'panda_group'. The server is 192.168.99.100
and your username and password is user1 and password2

```
curl -i -u "user1:password2" 192.168.99.100:8000/groups/create_group/ --data "groupname=panda_group"
```

### Add a file to a group

Add File allow you to add a file to a group. Both file and group needs to exist on the server.
(It will return error message if one or both of them is not.)

```
curl -u "username:password" [signalserver IP]:8000/groups/add_file -data="groupname=[your groupname]&filename=[your filename]"
```
Example:
You want to add a file named 'cucumber.gocart.xml.gz' 'panda_group'. The server is 192.168.99.100
and your username and password is user1 and password2

```
curl -i -u "user1:password2" 192.168.99.100:8000/groups/add_file/ --data "groupname=panda_group&filename=cucumber.gocart.xml.gz"
```

# For Developers

Congratulations for reading this far!

So you want to customize or change SignalServer or contribute, here is what else you need to know.

## Pre-Requisite

- Be able to install Docker, have a basic understanding of what Docker is, and be able to do basic system administration.

If you're unfamiliar with Docker or need a refresher, please review before proceeding.

## Docker Video Tutorial

The Docker video tutorial can be found [here](https://www.youtube.com/watch?v=bV5vbNK3Uhw&list=PLkA60AVN3hh_6cAz8TUGtkYbJSL2bdZ4h).

Also, please review this `docker-compose` tutorial for Wordpress (and please actually do deploy the Wordpress site by yourself). This project depends on `docker-compose`. So it is good to have a basic understanding.

Welcome back. Assuming you watched at least some of the tutorials, followed along the basics, and you also deployed a Wordpress site, now you know how to deploy a web application by single bash file.

I hope you've enjoyed your Docker journey so far. Let me now explain SignalServer's architecture overall. There are roughly three components of this system. Frontend, backend, and queue system. I will list these below but they are all put together by Docker and `docker-compose`. So you don't have to do any configuration for each of the application.

- Frontend - Bower Packagemement, Node Server (Bower's dependency)
             bootstrap, d3, jquery (all frontend assets are installed by bower)

- Backend - Django and Django RestFramework, Porgress (database)

- Queue System - Celery, Rabbit MQ, Redis

When you open the docker-compose.yml file, you'll see that this application uses 5 Docker containers to put these applications together. (Also, you can easily add one more worker for your queue system by changing docker-compose.yml e.g. your CPU utilization is low with one queue.)

Lastly, I recommend using Docker, but it is not an absolute requirement. You are free to choose whatever development environment you like. Just to make sure it works with entire system at the end of the day.

Good luck and Have fun!
