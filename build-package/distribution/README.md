tests for liveblog
==============

####if u don't trust us:

```sh
$ sudo useradd superdesk -b /opt -m
$ sudo su superdesk
```

##prerequesites

#####debian 7 or ubuntu 12.10

```sh
$ sudo apt-get install exiv2 ffmpeg graphicsmagick python3 python3-pip
```

#####newer versions of ubuntu/debian which are not shipped with python 3.2

```sh
$ sudo apt-get install exiv2 ffmpeg graphicsmagick python3-pip
```
and next follow python building instructions below

###building python 3.2

```sh
$ cd /tmp
$ wget http://www.python.org/ftp/python/3.2/Python-3.2.tgz
$ tar jxf ./Python-3.2.tgz
$ cd ./Python-3.2
$ ./configure --prefix=/opt/superdesk/python32
$ make && sudo make install
```

#####archlinux or manjaro

```sh
$ yaourt -S exiv2 ffmpeg graphicsmagick python32 python-pip
```

#installing

```sh
$ cd /opt/superdesk/
$ unzip liveblog.zip
```
next if your distro have python 3.2:
```sh
$ virtualenv -p python3.2 env
```
or if u was installed it manually to superdesk folder:
```sh
$ virtualenv -p /opt/superdesk/python32/bin/python3.2 env
```

```sh
$ source env/bin/activate
$ cd ./liveblog
$ pip install -r requirements.txt
```

#configuration

```sh
$ python application.py -dump
$ cp -f plugins-linux.properties plugins.properties
```
and next edit them if u need (ie change IPs, etc)

#running

```sh
$ python application.py
```

and open in your browser
```
http://localhost:8080/content/lib/core/start.html
```

