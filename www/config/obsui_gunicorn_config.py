# obsui gunicorn config

bind = "0.0.0.0:8090"
workers = 4

loglevel = 'info'

capture_output = True

errorlog = "/opt/starbug.com/logs/obsui-error.log"
accesslog = "/opt/starbug.com/logs/obsui-access.log"

forwarded_allow_ips = "*"
