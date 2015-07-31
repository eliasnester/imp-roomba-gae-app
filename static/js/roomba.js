// message types
var MESSAGE_INFO = 'info';
var MESSAGE_ERROR = 'error';
var WEB_CLIENT_ID = 'YOUR_WEB_CLIENT_ID';
var SCOPES = 'https://www.googleapis.com/auth/userinfo.email';

var messageType = {
    info: "#info",
    error: "#error"
  };

// charging states:
var chargingStates = {
  0: "Not Charging",
  1: "Charging Recovery",
  2: "Charging",
  3: "Trickle Charging",
  4: "Waiting",
  5: "Charging Error"
};

var roomba_buttons = [
  '#clean',
  '#sleep',
  '#doc',
  '#status'
];

var signedIn = false;

function enableButtons(buttons) {

  for (var i = 0; i < buttons.length; i++){
    $(buttons[i]).attr({'disabled': false});
    $(buttons[i]).click(buttonClickHandler);
  }
}

function getStatus(){

  displayMessage("Requesting data from server...", MESSAGE_INFO);
  gapi.client.roomba_api.cmd.sendCommand({'command': 'status'}).execute(function(resp) {
    if (!resp.code){
      hideMessage(MESSAGE_INFO);
      $('#status').attr({'disabled': false}); //ok this is bad FIXME 

      if (resp.result.result === 'RESULT_ERROR'){
        displayMessage(resp.error_message, MESSAGE_ERROR);
      } else {
        // update charging state data
        data = JSON.parse(resp.data);
        $('#charging_state').html(chargingStates[data.currentData.chargingState]);
        charge = Math.round((data.currentData.charge * 100)/data.currentData.capacity);
        $('#battery_remaining').html(charge + '%');
        updateProgressBar(charge);

        if (data.currentData.doc_state === true){
            $('#docking_state').html("connected");
        } else {
          $('#docking_state').html("disconnected");
        }
      }
    }
  });
}

function buttonClickHandler(){

    sendRoombaCommand(this.id);
    $(this).attr({disabled: true});
}

function sendRoombaCommand(cmd){

  hideMessage(MESSAGE_ERROR);
  displayMessage("Sending command: " + cmd , MESSAGE_INFO);

  if (cmd != 'status'){
    gapi.client.roomba_api.cmd.sendCommand({'command':cmd}).execute(function(resp) {

      if (!resp.code){
        hideMessage(MESSAGE_INFO);
        $('#'+cmd).attr({'disabled': false});

        if (resp.result.result === 'RESULT_ERROR'){
              displayMessage(resp.error_message + ' ' + resp.command, MESSAGE_ERROR);
        } else {
            displayMessage('Command executed successfully', MESSAGE_INFO, true);
            // TODO: update device state information with info received  from response
            // need to add this functionality to imp first
        }
      }
    });
  } else if (cmd === 'status') {
    getStatus();
  }
}

function displayMessage(message, type, autoclose, timeout){

  autoclose = autoclose || false;
  timeout = timeout || 2000;

  $(messageType[type]).html(message);
  $(messageType[type]).show();

  if (autoclose){
    window.setTimeout(function() { hideMessage(type); }, timeout);
  }

}

function hideMessage(type){

  $(messageType[type]).hide();

  // if (type === 'info'){
  //   $('#info').hide();
  // } else if (type === 'error') {
  //   $('#error').hide();
  // }
}

function updateProgressBar(value){

  if (value > 70){
    document.getElementById("progress_bar").className = 'progress-bar progress-bar-success';
  } else if (value > 40 & value < 70 ) {
    document.getElementById("progress_bar").className = 'progress-bar progress-bar-warning';
  } else if (value < 40) {
    document.getElementById("progress_bar").className = 'progress-bar progress-bar-danger';
  }
  $('#progress_bar').css('width', value+'%').attr('aria-valuenow', value);
}

function userAuthed(){

  var request = gapi.client.oauth2.userinfo.get().execute(function(resp) {
    if (!resp.code) {
      signedIn = true;
      getStatus();
      enableButtons(roomba_buttons);
      //document.getElementById('signinButton').innerHTML = 'Sign out';
      //document.getElementById('authedGreeting').disabled = false;
    } else {
      signin(false, userAuthed);
    }
  });
}

function signin(mode, callback) {

  gapi.auth.authorize ( {
      client_id:  WEB_CLIENT_ID,
      scope:  SCOPES, immediate: mode
    },
    callback);
}

function init(apiRoot) {

  // Loads the OAuth and helloworld APIs asynchronously, and triggers login
  // when they have completed.
  var apisToLoad;
  var callback = function() {

    if (--apisToLoad === 0) {
      signin(true, userAuthed);
    }
  };
  apisToLoad = 2; // must match number of calls to gapi.client.load()
  gapi.client.load('roomba_api', 'v1', callback, apiRoot);
  gapi.client.load('oauth2', 'v2', callback);
}
