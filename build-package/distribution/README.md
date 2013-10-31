Installing Superdesk
============================

+ [prerequisites](#prerequisites)
    - [debian/ubuntu](#debian-7-or-ubuntu-1204-1210)
    - [redhat/centos/sles](#redhatcentossles)
    - [arch/manjaro](#archlinux-or-manjaro)
+ [Installing Superdesk](#installing-superdesk)
+ [Configuring Superdesk](#configuring-superdesk)
+ [Running Superdesk](#running-superdesk)


## Prerequisites

### Debian 7 or Ubuntu 12.04, 12.10

1. Install necessary software:

	$ sudo apt-get install exiv2 ffmpeg graphicsmagick python3 python3-pip python-virtualenv

### Newer versions of ubuntu/debian which are not shipped with python 3.2

1. Install necessary software:

	$ sudo apt-get install exiv2 ffmpeg graphicsmagick python3-pip python-virtualenv

1. Build and install python 3.2

        $ cd /tmp
        $ wget http://www.python.org/ftp/python/3.2/Python-3.2.tgz
        $ tar xf ./Python-3.2.tgz
        $ cd ./Python-3.2
        $ ./configure --prefix=/opt/superdesk/python32
        $ make && sudo make install

### Redhat/Centos/sles


1. Add repositories for ffmpeg and GraphicsMagick:

        $ rpm -Uvh http://pkgs.repoforge.org/rpmforge-release/rpmforge-release-0.5.3-1.el6.rf.x86_64.rpm 
        $ rpm --import http://apt.sw.be/RPM-GPG-KEY.dag.txt
        $ rpm -Uvh http://download.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
        $ rpm --import https://fedoraproject.org/static/0608B895.txt

1. Install necessary software:

        # yum groupinstall "Development tools"
        # yum install exiv2 ffmpeg GraphicsMagick zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel

1. Build and install python 3.2

        $ cd /tmp
        $ wget http://pypi.python.org/packages/source/d/distribute/distribute-0.6.35.tar.gz --no-check-certificate
        $ tar xf distribute-0.6.35.tar.gz
        $ cd distribute-0.6.35
        $ /opt/superdesk/python32/bin/python3.2 setup.py install
        $ /opt/superdesk/python32/bin/easy_install-3.2 pip virtualenv

### Archlinux or Manjaro

1. Install necessary software:

        $ yaourt -S exiv2 ffmpeg graphicsmagick python32 python-pip python-virtualenv

## Installing Superdesk


1. Add the Superdesk user

        $ sudo useradd superdesk -b /opt -m
        $ sudo su superdesk

1. Change to `/opt/superdesk` and unzip `liveblog.zip`

	$ cd /opt/superdesk/
	$ unzip liveblog.zip

1. Create a python virtual environment using one of the following methods:

    * If your distro has python 3.2:

            $ virtualenv -p python3.2 env

    * If you installed Python 3.2 manually in the ``superdesk`` folder:

            $ virtualenv -p /opt/superdesk/python32/bin/python3.2 env

    * If you installed ``virtualenv`` manually in the ``superdesk`` folder:

            $ ./python32/bin/virtualenv-3.2 -p /opt/superdesk/python32/bin/python3.2 env

1. Activate the python virtual environment and install the requirements

	    $ source env/bin/activate
	    $ cd ./liveblog
	    $ pip install -r requirements.txt

## Configuring Superdesk

1. Create a configuration file

        $ python application.py -dump
        $ cp -f plugins-linux.properties plugins.properties

1. Edit the configuration file and change the IP address


## Running Superdesk

1. Run ``application.py

         $ python application.py

2. Open the following URL in your browser

         http://localhost:8080/content/lib/core/start.html
