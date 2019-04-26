============================
 Manually Installing Harvest
============================
--------------------
 Ubuntu
--------------------
1. Install transmission-daemon
    1. ``sudo apt install transmission-daemon``
    2. ``sudo service transmission-daemon disable``
2. Clone Harvest and Alcazard git
    1. Clone the Harvest GitHub repo in a directory of your choice. These instructions pertain to the home directory ``~/``
        - ``cd ~/``
        - ``git clone https://github.com/harvest-project/harvest.git``
    2. Clone the Alcazard GitHub repo **inside** the Harvest directory
        - ``cd ~/harvest``
        - ``git clone https://github.com/harvest-project/alcazard.git``
3. Install Python virtualenv
    1. Install the virtualenv package
        - ``sudo pip3 install virtualenv``
    2. Create the virtual environments inside **both** the Harvest and Alcazard directories
        - ``cd ~/harvest``
        - ``virtualenv -p python3 venv``
        - ``cd ~/harvest/alcazard``
        - ``virtualenv -p python3 venv``
4. Install dependencies
    1. Harvest dependencies
        - ``cd ~/harvest``
        - ``pip3 install -r requirements.txt``
    2. Alcazard dependencies
        - ``cd ~/harvest/alcazard``
        - ``pip3 install -r requirements.txt``
5. Install and configure PostgreSQL
    1. Install the PostgreSQL packages
        - ``sudo apt install postgresql postgresql-contrib``
    2. Configure PostgreSQL to start up upon bootup then manually start it
        - ``sudo update-rc.d postgresql enable``
        - ``sudo service postgresql start``
    3. Create a PostgreSQL user; this can be any desired user
        - ``sudo -u postgres createuser USER``
    4. Create the SQL database. These instructions use "harvest" as the db name
        - ``sudo -u postgres createdb --owner USER harvest``
6. Create a file named ``django_env`` in ~/harvest
        - Paste these contents inside the file ``DJANGO_DB=postgres:///harvest``
7. Migrate the database
    - ``./manage.py migrate``
8. Install nodesource
    - ``wget https://deb.nodesource.com/setup_10.x``
    - ``sudo ./setup_10.x``
    - ``sudo apt install nodejs``
    - ``cd /harvest``
    - ``npm install``
    - ``npm run build``
