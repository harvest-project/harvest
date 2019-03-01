function showMessage(message) {
    let messageElement = document.querySelector('#session_sync_message');
    if (!messageElement) {
        messageElement = document.createElement('tr');
        messageElement.id = 'session_sync_message';
        messageElement.innerHTML = '<td colspan="2" align="right" id="message_holder"></td>';
        document.querySelector('#loginform > table > tbody > tr:nth-child(3)')
            .insertAdjacentElement('afterend', messageElement);
    }
    messageElement.querySelector('#message_holder').textContent = message;
}

if (document.title === 'Bibliotik / Login') {
    console.log('Detected login page. Requesting login from background script...');
    showMessage('Trying Harvest login, please hold...');
    chrome.runtime.sendMessage(
        {type: messages.requestLogin},
        function(response) {
            console.log('Get response from background script: ' + response.type);
            if (response.type === messages.loginSuccessful) {
                showMessage('Login successful, please wait...');
                window.location.reload();
            } else if (response.type === messages.loginDisabled) {
                showMessage('Harvest login is disabled from options.');
            } else if (response.type === messages.loginFailed) {
                showMessage('Unable to login using Harvest.');
            }
        },
    );
}
