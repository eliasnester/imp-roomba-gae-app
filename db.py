import logging

from google.appengine.ext import ndb


class AccountSettings(ndb.Model):
    """Accound settings DB model to keep roomba settings for user"""
    userid = ndb.StringProperty()
    agent_url = ndb.StringProperty()
    device_mac = ndb.StringProperty()

    @classmethod
    def get_user_by_id(cls, user_id):
        return cls.query(cls.userid == user_id)


class AccountSettingsHelper():
    """add new user to a database if user is not yet created
        will create [UsersNdbModel(key=Key('UsersNdbModel', 6473924464345088), user_id=u'185804764220139124118', user_role=u'admin')]
    """

    def add_new_user(self, user_id):
        usr = AccountSettings(key=ndb.Key(AccountSettings, user_id))
        usr.userid = user_id
        usr.put()

    def user_exists(self, user_id):
        """Check if user already exists
        Returns: True if exists False otherwise
        """

        qry = AccountSettings().get_user_by_id(user_id)
        res = qry.fetch()
        if res:
            return True
        else:
            return False

    def update_device_information(self, user_id, agent_url=None, device_mac=None):
        """ update agent url and/or device_mac """

        if self.user_exists(user_id):

            usr_key = ndb.Key(AccountSettings, user_id)
            usr = usr_key.get()
            if agent_url:
                usr.agent_url = agent_url
            if device_mac:
                usr.device_mac = device_mac
            usr.put()
            return True
        else:
            logging.error("Cannot update information for non-existing user")
            return False

    def get_user_info(self, user_id):
        """ Returns information about user form db"""

        if self.user_exists:
            usr_key = ndb.Key(AccountSettings, user_id)
            usr = usr_key.get()
            return usr
        else:
            logging.error("User %s doesn't exist in db" % user_id)
