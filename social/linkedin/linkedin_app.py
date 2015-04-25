# # -*- coding: utf-8 -*-

############################
# Developer Authentication
############################

from linkedin import linkedin # refer to http://ozgur.github.io/python-linkedin/
import sys
sys.path.append("config");
import apiconf

# Define CONSUMER_KEY, CONSUMER_SECRET,
# USER_TOKEN, and USER_SECRET from the credentials
# provided in your LinkedIn application
CONSUMER_KEY = apiconf.CONSUMER_KEY
CONSUMER_SECRET = apiconf.CONSUMER_SECRET
USER_TOKEN = apiconf.USER_TOKEN
USER_SECRET = apiconf.USER_SECRET
RETURN_URL = 'http://localhost:8000'

# Instantiate the developer authentication class
authentication = linkedin.LinkedInDeveloperAuthentication(CONSUMER_KEY, CONSUMER_SECRET,
                                                          USER_TOKEN, USER_SECRET,
                                                          RETURN_URL, linkedin.PERMISSIONS.enums.values())
# Pass it in to the app...
application = linkedin.LinkedInApplication(authentication)
# Use the app....
print application.get_profile()
print application.get_connections()
print application.search_profile(selectors=[{'people': ['first-name', 'last-name']}], params={'keywords': 'sundy zhang'})
