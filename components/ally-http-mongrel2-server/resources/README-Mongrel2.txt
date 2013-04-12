IMPORTANT NOTE: We currently recommend the installation of Live Desk with Mongrel2 only for advanced users, i.e. people who
are well versed in server administration.

The ZeroMQ library is not part of the ally-py distribution like SQLAlchemy for instance, this is because ZeroMQ uses native
coding that needs to be compiled. So the first steps in using the ZeroMQ and Mongrel2 servers are the installation of these
tools. The described installations steps have been made on Ubuntu 12.04 but they should work fine on any Debian based
distributions.

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
	mv v1.8.0 mongrel2-1.8.0.tar.gz
	tar -xzvf mongrel2-1.8.0.tar.gz
	cd zedshaw-mongrel2-bc721eb
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

Open a new terminal and move to distribution:
	cd ../rest_api/superdesk/distribution

And then start the application (-OO is for production mode):
	python3 -OO application.py
	
If defaults are used this will start the ally py application using an in processor communication protocol, the application
is single threaded and will only consume on processor from the machine, in order to add more instances that are load
balanced by ZeromMQ you just need to start the application again, but before this we need to adjust some configurations
in order to avoid unnecessary operations that are done by ally-py.
So we will call the started application as being the main application and the next applications that we will start we call
them as being support application.

Creating support application configurations
-----------------------------------------------------------------------------------------------

So we already have the "application.properties" and "plugins.properties" from the main application:
Open a new terminal and move to distribution:
	cd ../rest_api/superdesk/distribution
we just need to create copies for the support application:
	cp application.properties application_support.properties
	cp plugins.properties plugins_support.properties

Now we need to adjust the "application_support.properties", change the following configurations to:
	configurations_file_path: plugins_support.properties

And in "plugins_support.properties", change the following configurations to:
	publish_gui_resources: false
this is to prevent the unnecessary publication of client files again by the support applications
	perform_cleanup: false
this prevents the superdesk authorization to clean the expired sessions and login tokens by the support applications

Starting support SuperDesk
-----------------------------------------------------------------------------------------------

Now simply start the application (-OO is for production mode):
	python3 -OO application.py --ccfg application_support.properties

You can start now as many support applications as you need but you should keep this number less or equal with the number
of CPUs that the computer has.
