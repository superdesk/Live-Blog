Mongrel2 should be installed by people who now what they are doing.
The ZeroMQ library is not part of the ally-py distribution like SQLAlchemy for instance, this is because ZeroMQ uses native
coding that needs to be compiled. So the first steps in using the ZeroMQ and Mongrel2 servers are the installation of this
tools. The described installations steps have been made on lubuntu 12.04 but they should work fine on any ubuntu.

Installing ZeroMQ
-----------------------------------------------------------------------------------------------

First we fetch the zeromg POSIX tarball, you can access "http://www.zeromq.org/intro:get-the-software" and download the 
POSIX tarball or:
	wget http://download.zeromq.org/zeromq-3.2.1-rc2.tar.gz

The we insall the zeromq:
	tar -xzvf zeromq-3.2.1-rc2.tar.gz
	cd zeromq-3.2.1/
	./configure 
	make
	sudo make install

Installing Mongrel2
-----------------------------------------------------------------------------------------------
	
Now we have the zeromq installed, we need now sqlite3 for Mongrel2 web server, this is in case you do not have it installed
already, attention you need also the dev version:
	sudo apt-get install sqlite3
	sudo apt-get install libsqlite3-dev
	
We install now the Mongrel2 web server, you can also check the steps at "http://mongrel2.org/wiki/quick_start.html":
	wget https://github.com/zedshaw/mongrel2/tarball/v1.8.0
	tar -xzvf mongrel2-1.8.0.tar.gz
	cd mongrel2-1.8.0/
	make clean all
	sudo make install
We will continue with Mongrel2 latter on.

Installing pyzmq
-----------------------------------------------------------------------------------------------
	
You also need a python3.2:
	sudo apt-get install python3
	sudo apt-get install python3-dev
	
You also need the python setup tools if you don't have them:
	sudo apt-get install python3-setuptools
	
After this we just easy install pyzmq:
	sudo easy_install3 pyzmq
When I installed pyzmq I get an error at the end:

	File "/usr/local/lib/python3.2/dist-packages/pyzmq-2.2.0.1-py3.2-linux-x86_64.egg/zmq/green/core.py", line 117
	    except gevent.Timeout, t:
	                         ^
	SyntaxError: invalid syntax
	
just ignore this.

Configuring superdesk
-----------------------------------------------------------------------------------------------

 We consider that you already have an ally-py distribution so we whon't got through the
steps of getting the superdesk. We consider the path for superdesk distribution as being:
	"../rest_api/superdesk/distribution"

Let use the distribution as the root folder.
	cd ../rest_api/superdesk/distribution

First we create the configuration (properties) files for superdesk:
	python3 application.py -dump
We now have in the distribution folder two new files "application.properties" and "plugin.properties", we need to adjust some
configurations here.

Now we tell ally-py to prepare the workspace for Mongrel2:
	python3 application.py -cfg-mongrel2
This will create the required folders and update the configurations accordingly

Starting Mongrel2
-----------------------------------------------------------------------------------------------

Change the root directory to the distribution workspace:
	cd workspace

Now we configure Mongrel2:
	m2sh load -config ally.conf

And then start Mongrel2:
	m2sh start -host localhost
	
Starting SuperDesk
-----------------------------------------------------------------------------------------------

Move to distribution:
	cd ..

And then start the application
	python3 application.py