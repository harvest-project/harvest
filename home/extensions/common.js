const messages = {
    requestLogin: 'requestLogin',
    loginSuccessful: 'loginSuccessful',
    loginFailed: 'loginFailed',
    loginDisabled: 'loginDisabled',
};

function getApiUrl(url, endpoint) {
    url = url.replace(/\/$/, '');
    return url + endpoint;
}

async function performGET(endpoint, options) {
    const {url, token} = await fetchConfig();
    const resp = await fetch(
        getApiUrl(url, getApiUrl(endpoint)),
        {
            headers: {
                'Authorization': 'Token ' + token,
            },
            ...options,
        },
    );
    return resp.json();
}

async function performPUT(endpoint, options) {
    const {url, token} = await fetchConfig();
    const resp = await fetch(
        getApiUrl(url, endpoint),
        {
            method: 'PUT',
            headers: {
                'Authorization': 'Token ' + token,
                'Content-Type': 'application/json',
            },
            ...options,
        },
    );
    return resp.json();
}

function getSessionCookie() {
    return new Promise((resolve, reject) => {
        chrome.cookies.get({
            url: 'https://bibliotik.me/',
            name: 'id',
        }, function(cookie) {
            resolve(cookie);
        });
    });
}

function setCookie(cookie) {
    return new Promise((resolve, reject) => {
        chrome.cookies.set(cookie, setCookie => {
            if (setCookie === null) {
                reject(chrome.runtime.lastError);
            } else {
                resolve(setCookie);
            }
        });
    });
}

function serializeCookie(cookie) {
    return {
        name: cookie.name,
        value: cookie.value,
        domain: cookie.domain,
        path: cookie.path,
        http_only: cookie.httpOnly,
        expires: Math.round(cookie.expirationDate),
        secure: cookie.secure,
    }
}

function deserializeCookie(cookieData) {
    return {
        url: 'https://bibliotik.me/',
        name: cookieData.name,
        value: cookieData.value,
        domain: cookieData.domain,
        path: cookieData.path,
        httpOnly: cookieData.http_only,
        expirationDate: cookieData.expires,
        secure: cookieData.secure,
    }
}

function fetchConfig() {
    return new Promise((resolve, reject) => {
        chrome.storage.local.get(
            {
                url: '',
                token: '',
                autoLogin: true,
            },
            async ({url, token, autoLogin}) => {
                if (!url || !token) {
                    reject('Please configure both URL and token.');
                }
                resolve({url, token, autoLogin});
            },
        );
    });
}

async function ping() {
    return await performGET('/api/ping');
}

async function syncCookies(allowReceive = true) {
    const cookie = await getSessionCookie();
    const cookies = [];
    if (cookie) {
        cookies.push(serializeCookie(cookie));
    }
    const response = await performPUT('/api/plugins/bibliotik/cookies', {
        body: JSON.stringify({
            cookies: cookies,
        }),
    });

    if (allowReceive) {
        for (const respCookie of response.cookies) {
            if (respCookie.name === 'id' && (!cookie || respCookie.value !== cookie.value)) {
                await setCookie(deserializeCookie(respCookie));
            }
        }
    }

    return response.cookies.length > 0;
}
