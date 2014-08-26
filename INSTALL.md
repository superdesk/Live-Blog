Installing LiveBlog
============================

+ [Prerequisites](#prerequisites)
+ [Installation](#installation)
+ [Configuration](#configuration)
+ [Running LiveBlog](#running-liveblog)
+ [Logging in](#logging-in)


The officially supported platform is Ubuntu and Python3.2. However the application can be installed on other OSs and below are provided the install instructions.

## Prerequisites


### Debian 7 or Ubuntu 12.04 LTS

Install necessary software:

    $ sudo apt-get install exiv2 ffmpeg graphicsmagick python3 git


### Newer versions of ubuntu/debian which are not shipped with python 3.2

1. Install necessary software:

        $ sudo apt-get install exiv2 ffmpeg graphicsmagick git

2. Build and install python 3.2 (better create a package if you know how)

        $ cd /tmp
        $ wget http://www.python.org/ftp/python/3.2.5/Python-3.2.5.tgz
        $ tar xf ./Python-3.2.5.tgz
        $ cd ./Python-3.2.5
        $ ./configure --prefix=/opt/python32
        $ make
        $ sudo make install  # or 'sudo checkinstall' to automatically generate a package

### Other systems

LiveBlog also can run on other Linux distributions and also Windows and OS X as well.
But while it's not officially supported you can try to figure it out on your own or ask help on [sourcefabric forums] (https://forum.sourcefabric.org/categories/superdesk-dev).

        
## Installation
The folowing installation steps in generally are applicable to all OSs and any exception is specified.

1. Change to the directory you choose to install the application and clone Ally-Py's master branch there. (instead of `master` branch it will be better to use stabilized tag, like `2.0.1-stable`, go [here] (https://github.com/sourcefabric/Ally-Py/releases) for the list of versions)

        $ git clone https://github.com/sourcefabric/Ally-Py.git -b master ally-py
        
   >Note: 
   >Depending by your OS you can choose a different location to install the application like /opt, c:\, etc.
        
2. Change to `ally-py` directory and clone LiveBlog's master branch there to directory `live-blog`.  (instead of `master` use latest stable tag, like `2.0.1-stable`, list is [here] (https://github.com/superdesk/Live-Blog/releases))

        $ cd ally-py
        $ git clone https://github.com/superdesk/Live-Blog.git -b master live-blog

3. Change to `ally-py/live-blog` directory and build eggs by running the following command:

        $ cd live-blog
        $ ./build-eggs

4. Change to `ally-py/live-blog/distribution` directory and create the configuration files by running the following command:

        $ cd distribution
        $ python3.2 application.py -dump        
        

## Configuration

### Access from the Internet
In order to access the application from other machines the following changes need to be done:

1. Edit the `application.properties` file, search for
   the property `server_host` and change it to `0.0.0.0`
   
    ```
    E.g.: server_host: 0.0.0.0
    ```
2. Edit the `plugins.properties` configuration file, search for the
   properties `server_url` and `embed_server_url` and change them to `[machine_name_or_ip]:8080`
   
    ```
    E.g.: server_url: my.machine.domain.com:8080
    ```


### For distribustions other than debian/ubuntu

You also need to update the full paths to ffmpeg/exiv2/gm tools in `plugins.properties` configuration file (in `ally-py/live-blog/distribution` folder).

Here are the properties that should be changes and default values:
   
        thumbnailProcessor.ThumbnailProcessorGM.gm_path: /usr/bin/gm
        imageDataHandler.metadata_extractor_path: /usr/bin/exiv2
        audioDataHandler.ffmpeg_path: /usr/bin/ffmpeg
        videoDataHandler.ffmpeg_path: /usr/bin/ffmpeg

## Running LiveBlog

### Development server

It's generally are applicable to all OSs and any exception is specified. In `live-blog/distribution` execute:

    $ python3.2 application.py

### Development server (from sources)

As a developer you can run the application from sources by running the following command:

    $ cd ..
    $ python3.2 distribution/application.py -s sources.ini

From distribution/plugins delete the egg(s) for the plugins you are working on. 
   
If you are working with the liveblog embed (livedesk-embed plugin) make sure that `live-blog/plugins/livedesk-embed/gui-resources/scripts/js/core.min.js` is empty.

### Production server

In order to runn LiveBlog on production environment you need to use [mongrel2](http://mongrel2.org/).

In `application.properties` change `application_mode` from `devel` to `normal`:

```
application_mode: normal
```

and modify settings to use mongrel and specify sockets for it:
```
server_type: mongrel2
recv_ident: liveblog
recv_spec: ipc:///opt/run/recv-liveblog
send_ident: liveblog
send_spec: ipc:///opt/run/send-liveblog
workspace_path: /opt
```

And in mongrel configuration file add definition like:

```
<......>
main = Server(
    chroot="/opt",
<......>
    Host(
        name="liveblog",
        matching="liveblog.mydomain.com",
        routes={
    	'/resources/': Handler(
    	    send_spec='ipc://run/send-liveblog',
    	    send_ident='liveblog',
    	    recv_spec='ipc://run/recv-liveblog',
    	    recv_ident=''
    	)
        '/content/': Dir(
    	    base='ally-py/live-blog/distribution/workspace/shared/cdm/',
    	    index_file='/lib/core/start.html',
    	    default_ctype='text/plain'
    	)
        }
    )
<......>
```

>Instead of `/opt/` you can use any other path suitable for your system configuration.

You can go to [sourcefabric forums] (https://forum.sourcefabric.org/categories/superdesk-dev) for more info.

## Logging in
Log in to following URL in your browser using credentials `admin/a`:

```
http://localhost:8080/content/lib/core/start.html
```

And here is an embed example:

```
http://localhost:8080/content/lib/livedesk-embed/index.html?theme=default&id=1
```
