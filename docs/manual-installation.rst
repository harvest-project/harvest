============================
 Manually Installing Harvest
============================
--------------------
 Installation Steps
--------------------
Ubuntu
######
1. Install transmission-daemon
    1. ``sudo apt install transmission-daemon``
    2. ``sudo service transmission-daemon disable``
2. Clone Harvest and Alcazard git
    1. Clone the Harvest GitHub repo in a directory of your choice. These instructions pertain to the home directory ~/
        - ``cd ~/``
        - ``git clone https://github.com/harvest-project/harvest.git``
    2. Clone the Alcazard GitHub repo **inside** the Harvest directory
        - ``cd ~/harvest``
        - ``git clone https://github.com/harvest-project/alcazard.git``
3. Install Python virtualenv
    1. Install python3 pip
        - ``sudo apt install python3-pip``
    2. Install the virtualenv package
        - ``sudo pip3 install virtualenv``
    3. Create the virtual environments inside **both** the Harvest and Alcazard directories
        - ``cd ~/harvest``
        - ``virtualenv -p python3 venv``
        - ``cd ~/harvest/alcazard``
        - ``virtualenv -p python3 venv``
4. Install dependencies
    1. ``cd ~/harvest``
    2. ``pip3 install -r requirements.txt``
    3. ``cd ~/harvest/alcazard``
    4. ``pip3 install -r requirements.txt``
