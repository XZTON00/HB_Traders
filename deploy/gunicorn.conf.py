# Gunicorn configuration for H.B. Trader's (hbtraders.com)
#
# Usage (also wired into deploy/hbtrader.service):
#   gunicorn -c deploy/gunicorn.conf.py hbtrader.wsgi:application
#
# Run from the project root (where manage.py lives) so relative paths below
# resolve correctly, or adjust the paths if you deploy elsewhere.

import multiprocessing
import os

# --- Socket ---
# Bind to a Unix socket; Nginx will proxy to this. Faster and more secure
# than binding to a TCP port on localhost.
bind = "unix:/run/hbtrader/gunicorn.sock"

# --- Workers ---
# (2 x CPU cores) + 1 is Gunicorn's recommended starting point.
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
threads = 2
timeout = 60
graceful_timeout = 30
keepalive = 5

# --- Process naming ---
proc_name = "hbtrader"

# --- Logging ---
accesslog = "/var/log/hbtrader/gunicorn-access.log"
errorlog = "/var/log/hbtrader/gunicorn-error.log"
loglevel = "info"
capture_output = True

# --- Reliability ---
# Restart workers periodically to avoid slow memory leaks; jitter avoids
# every worker restarting at the exact same moment.
max_requests = 1000
max_requests_jitter = 50

# --- User/group ---
# Uncomment and set if running gunicorn as root and want it to drop
# privileges itself (usually unnecessary since systemd already runs it as
# the hbtrader user — see deploy/hbtrader.service).
# user = "hbtrader"
# group = "www-data"

# --- Preload ---
# Loads the app once in the master process before forking workers: faster
# worker boot, lower memory (copy-on-write), at the cost of needing a full
# restart (not just reload) after code changes that affect app state.
preload_app = True
