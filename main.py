# file info
#

import webapp2
import jinja2
import os
import logging
import json

from db import AccountSettingsHelper
from google.appengine.api import users


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class MainHandler(webapp2.RequestHandler):

    def get(self):

        # Checks for active Google account session
        user = users.get_current_user()

        if user:

            logging.info("Current user: %s with id: %s" %(user, user.user_id()))
            template_values = {'user': user.nickname()
                              }
            template = JINJA_ENVIRONMENT.get_template(os.path.join('templates', 'main.html'))
            self.response.write(template.render(template_values))

        else:
            self.redirect(users.create_login_url(self.request.uri))

class SettingsHandler(webapp2.RequestHandler):

    def get(self):

        # Checks for active Google account session
        user = users.get_current_user()

        if user:
            # check if we have message in cookies

            cookie_message = self.request.cookies.get("message")
            if not cookie_message:
                info = ""
                error = ""
            else:
                self.response.delete_cookie("message")
                message = json.loads(cookie_message)
                info = message["info"] if "info" in message else ""
                error = message["error"] if "error" in message else ""

            # prepeare default template values
            template_values = { 'user': user.nickname(),
                                'agent_url': "",
                                'device_mac': "",
                                'info': info,
                                'error': error
                                }

            account = AccountSettingsHelper()
            user_id = user.user_id() 
            logging.info("Current user: %s with id: %s" %(user, user.user_id()))
            # check if user is already in DB, otehrwise add it
            if not account.user_exists(user_id):
                logging.info("User account doesn't exist for id %s" %user_id)
                try: 
                    account.add_new_user(user_id)
                except Exception, e:
                    logging.exception("Exception %s happened" %e)
            else:
                # if user exists get values form DB 
                usr = account.get_user_info(user_id)
                template_values['agent_url'] = usr.agent_url
                template_values['device_mac'] =  usr.device_mac

            logging.info("Generating template using values: %s" %template_values)

            template = JINJA_ENVIRONMENT.get_template(os.path.join('templates', 'settings.html'))
            self.response.write(template.render(template_values))
        # if user is not authenticated -> redirect to google auth page
        else:
            self.redirect(users.create_login_url(self.request.uri))

    def post(self):

        # TODO: add csrf protection
        user = users.get_current_user()

        if user:
            logging.info(" Processing POST. Got data: agent: %s mac: %s" %(self.request.get('agent_url'), self.request.get('device_mac')))
            logging.info("Is user admin: %s" %users.is_current_user_admin())
            account = AccountSettingsHelper()
            user_id = user.user_id()
            agent_url = self.request.get('agent_url')
            device_mac = self.request.get('device_mac')
            #TODO: data validation for  agent_url and device_mac values

            try:
                res = account.update_device_information(user_id, agent_url, device_mac )
            except Exception, e:
                    logging.exception("Exception %s happened" %e)
            
            if res:
                # redirect with success message 
                logging.info("Redirecting to settings")
                self.response.set_cookie("message", json.dumps({"info": "Success"}));
                self.redirect("/settings")
            else:
                # TODO: redrect with error message
                logging.error("Cannot update values")

        else:
            self.redirect(users.create_login_url(self.request.uri))



app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/settings', SettingsHandler)
], debug=True)
