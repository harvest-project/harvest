chrome.cookies.onChanged.addListener(function(changeInfo) {
    const cookie = changeInfo.cookie;

    if (changeInfo.cause === 'explicit' && cookie.name === 'id' && cookie.domain === '.bibliotik.me') {
        syncCookies(false);
    }
});

async function requestLoginHelper(sendResponse) {
    const {autoLogin} = await fetchConfig();
    if (!autoLogin) {
        sendResponse({type: messages.loginDisabled});
    } else if (await syncCookies()) {
        sendResponse({type: messages.loginSuccessful});
    } else {
        sendResponse({type: messages.loginFailed});
    }
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type && request.type === 'requestLogin') {
        requestLoginHelper(sendResponse);
        return true;
    }
});
