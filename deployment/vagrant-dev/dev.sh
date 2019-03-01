#!/usr/bin/env bash

set -e

tmux kill-session -t dev 2> /dev/null || true

tmux new-session -s dev -d
tmux \
     split-pane -t dev -h \; \
     split-pane -t dev -v \; \
     split-pane -t dev -h \; \
     select-layout tiled \; \
     send-keys -t dev:0.0 "source ~/venv/bin/activate" C-m "cd /vagrant" C-m "./manage.py runserver 0.0.0.0:8000" C-m \; \
     send-keys -t dev:0.1 "source ~/venv/bin/activate" C-m "cd /vagrant" C-m "./manage.py run_scheduler" C-m \; \
     send-keys -t dev:0.2 "source ~/venv/bin/activate" C-m "cd /vagrant/alcazard" C-m "./alcazard.py --state state/ run" C-m \; \
     send-keys -t dev:0.3 "cd /vagrant" C-m "npm run build -- --watch" C-m \; \
     attach-session -t dev
