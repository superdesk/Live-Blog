Installing LiveBlog
============================

+ [prerequisites](#prerequisites)
    - [debian/ubuntu](#debian-7-or-ubuntu-1204-1210)
    - [redhat/centos/sles](#redhatcentos)
    - [arch/manjaro](#archlinux-or-manjaro)
    - [win7/win8](#win7-or-win8)    
+ [Installing LiveBlog](#installing-liveblog)
+ [Configuring LiveBlog](#configuring-liveblog)
+ [Running LiveBlog](#running-liveblog)


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
        $ ./configure --prefix=/opt/python32
        $ make
        $ sudo make install  # or 'sudo checkinstall' to automatically generate a package
        
        
### Redhat/Centos

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
        $ ./configure --prefix=/opt/python32
        $ make
        $ sudo make install  # or 'sudo checkinstall' to automatically generate a package

        
        
### Archlinux or Manjaro

1. Install necessary software:

        $ yaourt -S exiv2 ffmpeg graphicsmagick python32 git

        
        
### Win

1. Install necessary software
   Download and install the tools from the following addresses:
        ffmpeg: http://www.ffmpeg.org/download.html
        exiv2: http://www.exiv2.org/download.html
        gm: http://www.graphicsmagick.org/INSTALL-windows.html
        
2. Install python 3.2
   Download and install the right version from the following address:
        https://www.python.org/download/releases/3.2


        
## Installing LiveBlog

1. Change to `/opt/` and clone Ally-Py's master branch there.

        $ cd /opt/
        $ sudo git clone https://github.com/sourcefabric/Ally-Py.git -b master ally-py
        
   Notes: 
        Depending by your OS you can choose a different location to install the application
        On win the sudo command is not applicable 
        
        
2. Change to `/opt/ally-py` and clone LiveBlog's master branch there.

        $ cd ./ally-py
        $ sudo git clone https://github.com/superdesk/Live-Blog.git live-blog

3. Change to /opt/ally-py/live-blog and build eggs by running the following command:

        $ cd ./live-blog
        $ ./build-eggs 
        (build-eggs.bat on win)

4. Create the configuration files by running the following command:

        $ python3.2 /opt/ally-py/live-blog/distribution/application.py -dump

5. Update the full paths to ffmpeg/exiv2/gm tools in `/opt/ally-py/live-blog/distribution/application.properties`.
   Here are the properties that should be changes and default values:
   
        thumbnailProcessor.ThumbnailProcessorGM.gm_path: /usr/bin/gm
        imageDataHandler.metadata_extractor_path: /usr/bin/exiv2
        audioDataHandler.ffmpeg_path: /usr/bin/ffmpeg
        videoDataHandler.ffmpeg_path: /usr/bin/ffmpeg
        
        

## Configuring LiveBlog

#### Access from the Internet
In order to access the application from other machines the following changes need to be done:

1. Edit the file '/opt/ally-py/live-blog/distribution/application.py', search for
   the property 'server_host' and change it to '0.0.0.0'
   E.g.: server_host: 0.0.0.0

2. Edit the file '/opt/ally-py/live-blog/distribution/application.py', search for the
   properties 'server_url' and 'embed_server_url' and change them to
   '[machine_name_or_ip]:8080
   E.g.: server_url: my.machine.domain.com:8080



## Running LiveBlog

1. Run Ally-Py REST server:

        $ python3.2 /opt/ally-py/live-blog/distribution/application.py
        
   As a developer you can run the application from sources by using start-sources.sh(start-sources.bat on win) script.


2. Log in to following URL in your browser using credentials `admin/a`:

        http://localhost:8080/content/lib/core/start.html

   And here is an embed example:

        http://localhost:8080/content/lib/livedesk-embed/index.html?theme=default&id=1
