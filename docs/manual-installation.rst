============================
 Manually Installing Harvest
============================
--------------------
 Ubuntu
--------------------
#. Install transmission-daemon
    #. ``sudo apt install transmission-daemon``
    #. ``sudo systemctl stop transmission-daemon.service``
#. Clone Harvest and Alcazard git
    #. Clone the Harvest GitHub repo in a directory of your choice. These instructions pertain to the home directory ``~/``
        - ``cd ~/``
        - ``git clone https://github.com/harvest-project/harvest.git``
    #. Clone the Alcazard GitHub repo **inside** the Harvest directory
        - ``cd ~/harvest``
        - ``git clone https://github.com/harvest-project/alcazard.git``
#. Install Python virtualenv
    #. Install the virtualenv package
        - ``sudo pip3 install virtualenv``
    #. Create the virtual environments inside **both** the Harvest and Alcazard directories
        - ``cd ~/harvest``
        - ``virtualenv -p python3 venv``
        - ``cd ~/harvest/alcazard``
        - ``virtualenv -p python3 venv``
#. Install dependencies
    #. Harvest dependencies
        - ``cd ~/harvest``
        - ``pip3 install -r requirements.txt``
    #. Alcazard dependencies
        - ``cd ~/harvest/alcazard``
        - ``pip3 install -r requirements.txt``
#. Install and configure PostgreSQL
    #. Install the PostgreSQL packages
        - ``sudo apt install postgresql postgresql-contrib``
    #. Start PostgreSQL and enable upon bootup
        - ``sudo systemctl start postgresql``
        - ``sudo systemctl enable postgresql``
    #. Create a PostgreSQL user; this can be any desired user
        - ``sudo -u postgres createuser USER``
    #. Create the SQL database. These instructions use "harvest" as the db name
        - ``sudo -u postgres createdb --owner USER harvest``
    #. Create a file named ``django_env`` in ~/harvest
            - Paste these contents inside the file ``DJANGO_DB=postgres:///harvest``
#. Migrate the database
    - ``./manage.py migrate``
#. Install Node.js
    #. Install Node.js from the official apt repos
        - ``wget https://deb.nodesource.com/setup_10.x``
        - ``sudo ./setup_10.x``
        - ``sudo apt install nodejs``
    #. Compile Harvest JS resources
        - ``cd ~/harvest``
        - ``npm install``
        - ``npm run build``
#. Run Alcazar
    - ``cd ~/harvest/alcazard``
    - ``source venv/bin/activate``
    - ``./alcazard.py --state state/ config``
    - ``./alcazard.py --state state/ run`` the default host is ``0.0.0.0:7001``
    - ``http://0.0.0.0:7001`` should display ``{"hello": "world"}``
#. Run Harvest
    #. Start Harvest Server
        - ``cd ~/harvest``
        - ``source venv/bin/activate``
        - ``./manage.py runserver`` while Alcazard is still running, the default host is ``127.0.0.1:8000``
            - ``./manage.py runserver HOST:PORT`` to specify host
        - ``http://127.0.0.1:8000`` should show the Harvest login page
    #. Create Harvest User
        - ``./manage.py create_harvest_superuser --exists-ok USER PASSWORD``
    #. Configure Alcazar Client (Either option works)
        a. Terminal
            - ``./manage.py config_alcazar_client``
        b. WebUI
            - Go to Harvest page
            - Log in with Harvest user created in steps above
            - Settings -> Harvest -> Alcazar Client
                - Base URL is the Alcazar host ``localhost:7001``
    #. Create Alcazar instance
        - Settings -> Alcazar -> Instances
            - Add Client
            - Choose desired Realm
            - Choose **Managed Transmission** for Instance Type
    #. Start Scheduler to periodically sync the Harvest database and Alcazar
        - ``./manage.py run_scheduler``

--------------------
 Troubleshooting
--------------------
#. ``transmissionrpc.error.TransmissionError: Request failed. Original exception: HTTPHandlerError, "HTTPHandlerError 401: Unauthorized"``
    - Transmission started on boot
        - Kill Transmission-daemon process
            - ``sudo systemctl stop transmission-daemon.service``
        - Disable Transmission-daemon automatic startup
            - ``sudo systemctl disable transmission-daemon.service``
