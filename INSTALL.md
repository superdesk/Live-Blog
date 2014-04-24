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

        $ sudo apt-get install exiv2 ffmpeg graphicsmagick python3 git

        
        
### Newer versions of ubuntu/debian which are not shipped with python 3.2

1. Install necessary software:

        $ sudo apt-get install exiv2 ffmpeg graphicsmagick git

2. Build and install python 3.2 (better create a package if you know how)

        $ cd /tmp
        $ wget http://www.python.org/ftp/python/3.2/Python-3.2.tgz
        $ tar xf ./Python-3.2.tgz
        $ cd ./Python-3.2
        $ ./configure --prefix=/opt/superdesk/python32
        $ make && sudo make install

        
        
### Redhat/Centos/sles

1. Add repositories for ffmpeg and GraphicsMagick:

        # rpm -Uvh http://pkgs.repoforge.org/rpmforge-release/rpmforge-release-0.5.3-1.el6.rf.x86_64.rpm 
        # rpm --import http://apt.sw.be/RPM-GPG-KEY.dag.txt
        # rpm -Uvh http://download.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
        # rpm --import https://fedoraproject.org/static/0608B895.txt

2. Install necessary software:

        # yum groupinstall "Development tools"
        # yum install exiv2 ffmpeg GraphicsMagick zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel

3. Build and install python 3.2

        $ cd /tmp
        $ wget http://www.python.org/ftp/python/3.2/Python-3.2.tgz
        $ tar xf ./Python-3.2.tgz
        $ cd ./Python-3.2
        $ ./configure --prefix=/opt/superdesk/python32
        $ make && sudo make install

        
        
### Archlinux or Manjaro

1. Install necessary software:

        $ yaourt -S exiv2 ffmpeg graphicsmagick python32 git

        
        
## Installing Superdesk

0. (optional) Add the Superdesk user

        $ sudo useradd superdesk -m -s /bin/bash

1. Change to `/opt/` and clone Ally-Py's master branch there.

        $ cd /opt/
        $ sudo git clone https://github.com/sourcefabric/Ally-Py.git -b master ally-py

2. Change to `/opt/ally-py` and clone Superdesk's liveblog16 branch there.

        $ cd ./ally-py
        $ sudo git clone https://github.com/sourcefabric/Superdesk.git -b liveblog16 superdesk

3. (optional) set rights to ally-py folder to superdesk user and switch to it:

        $ sudo chown superdesk -R /opt/ally-py
        $ sudo su superdesk

4. Change to /opt/ally-py/superdesk and build eggs by running the following command:

        $ cd ./superdesk
        $ ./build-eggs

5. Create the configuration files by running the following command:

        $ python3.2 /opt/ally-py/superdesk/distribution/application.py -dump

6. Update the full paths to ffmpeg/exiv2/gm tools in `/opt/ally-py/superdesk/distribution/application.properties`.
   Here are the properties that should be changes and default values:
   
        thumbnailProcessor.ThumbnailProcessorGM.gm_path: /usr/bin/gm
        imageDataHandler.metadata_extractor_path: /usr/bin/exiv2
        audioDataHandler.ffmpeg_path: /usr/bin/ffmpeg
        videoDataHandler.ffmpeg_path: /usr/bin/ffmpeg
        
        

## Configuring Superdesk

#### Access from the Internet
In order to access the application from other machines the following changes need to be done:

1. Edit the file 'superdesk/distribution/application.properties', search for
   the property 'server_host' and change it to '0.0.0.0'
   E.g.: server_host: 0.0.0.0

2. Edit the file 'superdesk/distribution/plugins.properties', search for the
   properties 'server_url' and 'embed_server_url' and change them to
   '[machine_name_or_ip]:8080
   E.g.: server_url: my.machine.domain.com:8080



## Running Superdesk

1. Run Ally-Py REST server:

        $ python3.2 /opt/ally-py/superdesk/distribution/application.py

2. Log in to following URL in your browser using credentials `admin/a`:

        http://localhost:8080/content/lib/core/start.html

   And here is an embed example:

        http://localhost:8080/content/lib/livedesk-embed/index.html?theme=default&id=1
