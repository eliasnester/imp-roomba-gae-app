import endpoints
import logging
import json
from google.appengine.api import urlfetch
from protorpc import messages
from protorpc import remote
from db import AccountSettingsHelper


WEB_CLIENT_ID = 'YOUR_WEB_CLIENT_ID'
CLIENT_ID_LIST = [WEB_CLIENT_ID, endpoints.API_EXPLORER_CLIENT_ID]

package = 'Roomba'


class CommandRequest(messages.Message):
    class Commands(messages.Enum):
        status = 1
        clean = 2
        sleep = 3
        doc = 4
        spot = 5
    command = messages.EnumField('CommandRequest.Commands', 1, default='status')


class CommandResponseMessage(messages.Message):
    class Result(messages.Enum):
        RESULT_OK = 1
        RESULT_ERROR = 2


class CommandResponse(messages.Message):

    class Result(messages.Enum):
        RESULT_OK = 1
        RESULT_ERROR = 2

    result = messages.EnumField('CommandResponse.Result', 1, default='RESULT_OK')
    command = messages.EnumField('CommandRequest.Commands', 2)
    data = messages.StringField(3)
    error_message = messages.StringField(4)


@endpoints.api(name='roomba_api', version='v1', allowed_client_ids=CLIENT_ID_LIST, scopes=[endpoints.EMAIL_SCOPE])
class RoombaApi(remote.Service):
    """Roomba Api API v1.0 test api"""

    @endpoints.method(CommandRequest, CommandResponse,
                      path='robot', http_method='GET',
                      name='cmd.sendCommand')
    def send_command(self, request):
        response = CommandResponse()
        response.result = CommandResponse.Result.RESULT_OK

        # Checks for active Google account session

        user = endpoints.get_current_user()
        logging.info("Current user: %s with id: %s" % (user, user.user_id()))

        if user:
            account = AccountSettingsHelper()
            user_id = user.user_id()

            # check if user exists in db
            if account.user_exists(user_id):
                    usr = account.get_user_info(user_id)
                    url = '%s/api/%s?command=%s' % (usr.agent_url, usr.device_mac, request.command)
                    logging.info("Submiting request to:  %s" % url)

                    try:
                        res = urlfetch.fetch(url)
                    except Exception:
                        res = None
                        pass

                    if res:
                        if res.status_code == 200:
                            logging.info("Got response: %s" % res.content)

                            res_json = json.loads(res.content)
                            response.command = CommandRequest.Commands(res_json['command'])

                            if res_json['result'] == 'ok':
                                response.result = CommandResponse.Result.RESULT_OK
                            else:
                                response.result = CommandResponse.Result.RESULT_ERROR
                                response.error_message = res_json['error']

                            if 'data' in res_json:
                                response.data = json.dumps(res_json['data'])
                        else:
                            response.result = CommandResponse.Result.RESULT_ERROR
                            response.error_message = '%s, %s' % (res.status_code, res.content)
                    else:
                        response.result = CommandResponse.Result.RESULT_ERROR
                        response.error_message = 'Cannot connect to server'
            # else if user not in db send error message as response
            else:
                response.result = CommandResponse.Result.RESULT_ERROR
                response.error_message = 'Cannot find agent url information in DB. Check your settings'

        # else if request came from non authorized user
        else:
            response.result = CommandResponse.Result.RESULT_ERROR
            response.error_message = 'Unauthorized'

        logging.info('Sending response: %s' % response)
        return response


APPLICATION = endpoints.api_server([RoombaApi], restricted=False)
