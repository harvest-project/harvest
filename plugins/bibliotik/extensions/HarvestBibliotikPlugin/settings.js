function saveOptions() {
    const url = document.getElementById('url').value,
        token = document.getElementById('token').value,
        autoLogin = document.getElementById('auto_login').checked;

    chrome.storage.local.set({
        url: url,
        token: token,
        autoLogin: autoLogin,
    }, function() {
        const status = document.getElementById('status');
        status.textContent = 'Connection settings saved.';
        setTimeout(() => status.innerHTML = '&nbsp', 5000);
    });
}

async function restoreOptions() {
    document.getElementById('save').addEventListener('click', saveOptions);
    document.getElementById('test_connection').addEventListener('click', testConnection);

    const {url, token, autoLogin} = await fetchConfig();
    document.getElementById('url').value = url;
    document.getElementById('token').value = token;
    document.getElementById('auto_login').checked = autoLogin;
}

async function testConnection() {
    const status = document.getElementById('connection_status');

    function showMessage(message) {
        status.textContent = message;
        setTimeout(() => status.innerHTML = '&nbsp', 5000);
    }

    let url, token;
    try {
        ({url, token} = await fetchConfig());

        const resp = await fetch(
            url + 'api/ping',
            {
                headers: {
                    'Authorization': 'Token ' + token,
                },
            },
        );
        if (resp.status !== 200) {
            let message = `Error connecting to Harvest, server returned ${resp.status}.`;
            try {
                const data = await resp.json();
                if (data.detail) {
                    message += ` Error: ${data.detail}`;
                }
            } catch {
            }
            throw message;
        }
    } catch (exception) {
        showMessage(exception);
        return;
    }

    try {
        await syncCookies();
    } catch (exception) {
        showMessage('Connection successful, but unable to sync cookies: ' + exception);
        return;
    }

    showMessage('Connection successful, cookies are synced.');
}

document.addEventListener('DOMContentLoaded', restoreOptions);
