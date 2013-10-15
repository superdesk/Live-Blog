superdesk install instuctions
==============

+ [prerequisites](#prerequisites)
  - [debian/ubuntu](#debian-7-or-ubuntu-1204-1210)
  - [redhat/centos/sles](#redhatcentossles)
  - [arch/manjaro](#archlinux-or-manjaro)
  - [building python 3.2](#building-python-32)
+ [installing](#installing)
+ [configuration](#configuration)
+ [running](#running)

####if u don't trust us:
```sh
$ sudo useradd superdesk -b /opt -m
$ sudo su superdesk
```

##prerequesites

#####debian 7 or ubuntu 12.04, 12.10

```sh
$ sudo apt-get install exiv2 ffmpeg graphicsmagick python3 python3-pip python-virtualenv
```

#####newer versions of ubuntu/debian which are not shipped with python 3.2

```sh
$ sudo apt-get install exiv2 ffmpeg graphicsmagick python3-pip python-virtualenv
```
and next follow python building instructions below

###building python 3.2

```sh
$ cd /tmp
$ wget http://www.python.org/ftp/python/3.2/Python-3.2.tgz
$ tar xf ./Python-3.2.tgz
$ cd ./Python-3.2
$ ./configure --prefix=/opt/superdesk/python32
$ make && sudo make install
```
#####redhat/centos/sles

```
##we need it for ffmpeg:
# rpm -Uvh http://pkgs.repoforge.org/rpmforge-release/rpmforge-release-0.5.3-1.el6.rf.x86_64.rpm # or other one depending your distirution
# rpm --import http://apt.sw.be/RPM-GPG-KEY.dag.txt

##and this one for GraphicsMagick:
# rpm -Uvh http://download.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
# rpm --import https://fedoraproject.org/static/0608B895.txt
```
if u don't like to add additional repos of course u can build ffmpeg and GraphicsMagick manually
```
# yum groupinstall "Development tools"
# yum install exiv2 ffmpeg GraphicsMagick zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel
```
next follow python 3.2 building instructions above
```sh
$ cd /tmp
$ wget http://pypi.python.org/packages/source/d/distribute/distribute-0.6.35.tar.gz --no-check-certificate
$ tar xf distribute-0.6.35.tar.gz
$ cd distribute-0.6.35
$ /opt/superdesk/python32/bin/python3.2 setup.py install
$ /opt/superdesk/python32/bin/easy_install-3.2 pip virtualenv
```

#####archlinux or manjaro

```sh
$ yaourt -S exiv2 ffmpeg graphicsmagick python32 python-pip python-virtualenv
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
or if u was installed manually to superdesk folder even virtualenv:
```sh
$ ./python32/bin/virtualenv-3.2 -p /opt/superdesk/python32/bin/python3.2 env
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
