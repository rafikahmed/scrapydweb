import sys 
import os
import logging

sys.path.insert(0, '/var/www/html/scrapydweb')
sys.path.append('/var/www/html/scrapydweb/my_env/lib/python3.8/site-packages')
sys.path.append('/var/www/html')


from scrapydweb import create_app
from scrapydweb.common import handle_metadata, authenticate
from flask import request


application = create_app()
application.config['DEFAULT_SETTINGS_PY_PATH'] = '/var/www/html/scrapydweb/default_settings.py'
application.config['SCRAPYDWEB_SETTINGS_PY_PATH'] = '/var/www/html/scrapydweb/default_settings.py'


main_pid = os.getpid()
application.config['MAIN_PID'] = main_pid
application.config['LOGPARSER_PID'] = main_pid
application.config['POLL_PID'] = main_pid

logger = logging.getLogger(__name__)
apscheduler_logger = logging.getLogger('apscheduler')

handle_metadata('main_pid', main_pid)

@application.context_processor
def inject_variable():
	SCRAPYD_SERVERS = application.config.get('SCRAPYD_SERVERS', []) or ['127.0.0.1:6800']
	SCRAPYD_SERVERS_PUBLIC_URLS = application.config.get('SCRAPYD_SERVERS_PUBLIC_URLS', None)
	return dict(
	SCRAPYD_SERVERS=SCRAPYD_SERVERS,
	SCRAPYD_SERVERS_AMOUNT=len(SCRAPYD_SERVERS),
	SCRAPYD_SERVERS_GROUPS=application.config.get('SCRAPYD_SERVERS_GROUPS', []) or [''],
	SCRAPYD_SERVERS_AUTHS=application.config.get('SCRAPYD_SERVERS_AUTHS', []) or [None],
	SCRAPYD_SERVERS_PUBLIC_URLS=SCRAPYD_SERVERS_PUBLIC_URLS or [''] * len(SCRAPYD_SERVERS),

	DAEMONSTATUS_REFRESH_INTERVAL=application.config.get('DAEMONSTATUS_REFRESH_INTERVAL', 10),
	ENABLE_AUTH=application.config.get('ENABLE_AUTH', False),
	SHOW_SCRAPYD_ITEMS=application.config.get('SHOW_SCRAPYD_ITEMS', True),
	)
@application.before_request
def require_login():
	if application.config.get('ENABLE_AUTH', False):
	    auth = request.authorization
	    USERNAME = str(application.config.get('USERNAME', ''))  # May be 0 from config file
	    PASSWORD = str(application.config.get('PASSWORD', ''))
	    if not auth or not (auth.username == USERNAME and auth.password == PASSWORD):
		return authenticate()


if __name__ == '__main__':
	application.run()
