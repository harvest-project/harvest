import Noty from 'noty';

export const messages = {
    requestLogin: 'onRequestLogin',
    loginSucceeded: 'loginSucceeded',
    loginFailed: 'loginFailed',
    loginDisabled: 'loginDisabled',
    getTorrentStatuses: 'onGetTorrentStatuses',
    getTorrentStatusesSuccess: 'getTorrentStatusesSuccess',
    getTorrentStatusesError: 'getTorrentStatusesError',
};

export class NotyHelper {
    static _noty(type, text) {
        return new Noty({
            type: type,
            text: text,
            timeout: 2000,
        }).show();
    }

    static alert(text, timeout) {
        return this._noty('alert', text);
    }

    static success(text) {
        return this._noty('success', text);
    }

    static error(text) {
        return this._noty('error', text);
    }

    static warning(text) {
        return this._noty('warning', text);
    }

    static info(text) {
        return this._noty('info', text);
    }
}

export class PluginHelper {
    static cookieUrl = null;
    static cookiesEndpoint = null;
    static initialConfig = {
        url: '',
        token: '',
        autoLogin: true,
    };

    getApiUrl(url, endpoint) {
        url = url.replace(/\/$/, '');
        return url + endpoint;
    }

    async fetch(endpoint, options) {
        const {url, token} = await this.fetchConfig();
        options.headers = options.headers || {};
        options.headers['Authorization'] = 'Token ' + token;
        const resp = await fetch(this.getApiUrl(url, endpoint), options);
        if (resp.status < 200 || resp.status >= 300) {
            throw resp;
        }
        return resp.json();
    }

    async performGET(endpoint, options) {
        return await this.fetch(endpoint, options);
    }

    async performPOST(endpoint, options) {
        return await this.fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                ...options,
            },
        );
    }

    async performPUT(endpoint, options) {
        return await this.fetch(endpoint, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                ...options,
            },
        );
    }

    getSessionCookie() {
        return new Promise((resolve, reject) => {
            chrome.cookies.get({
                url: this.constructor.cookieUrl,
                name: 'id',
            }, function (cookie) {
                resolve(cookie);
            });
        });
    }

    setCookie(cookie) {
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

    serializeCookie(cookie) {
        return {
            name: cookie.name,
            value: cookie.value,
            domain: cookie.domain,
            path: cookie.path,
            http_only: cookie.httpOnly,
            expires: Math.round(cookie.expirationDate),
            secure: cookie.secure,
        };
    }

    deserializeCookie(cookieData) {
        return {
            url: this.constructor.cookieUrl,
            name: cookieData.name,
            value: cookieData.value,
            domain: cookieData.domain,
            path: cookieData.path,
            httpOnly: cookieData.http_only,
            expirationDate: cookieData.expires,
            secure: cookieData.secure,
        };
    }

    fetchConfig(allowEmpty) {
        return new Promise((resolve, reject) => {
            chrome.storage.local.get(
                this.constructor.initialConfig,
                async ({url, token, autoLogin}) => {
                    if (!allowEmpty && (!url || !token)) {
                        reject('Please configure both URL and token.');
                    }
                    resolve({url, token, autoLogin});
                },
            );
        });
    }

    async ping() {
        try {
            await this.performGET('/api/ping');
        } catch (resp) {
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
    }

    async syncCookies(allowReceive = true) {
        const cookie = await this.getSessionCookie();
        const cookies = [];
        if (cookie) {
            cookies.push(this.serializeCookie(cookie));
        }
        const response = await this.performPUT(this.constructor.cookiesEndpoint, {
            body: JSON.stringify({
                cookies: cookies,
            }),
        });

        if (allowReceive) {
            for (const respCookie of response.cookies) {
                if (respCookie.name === 'id' && (!cookie || respCookie.value !== cookie.value)) {
                    await this.setCookie(this.deserializeCookie(respCookie));
                }
            }
        }

        return response.cookies.length > 0;
    }

    async testConnection() {
        await this.ping();

        try {
            await this.syncCookies();
        } catch (exception) {
            throw `Connection successful, but unable to sync cookies: ${exception}`;
        }

        return 'Connection successful, cookies are synced.';
    }

    async onRequestLogin(sendResponse) {
        let detail;
        try {
            const {autoLogin} = await this.fetchConfig();
            if (!autoLogin) {
                sendResponse({type: messages.loginDisabled});
            } else if (await this.syncCookies()) {
                sendResponse({type: messages.loginSucceeded});
            } else {
                detail = 'No working cookies received from server.';
            }
        } catch (exception) {
            detail = exception.toString();
        }
        sendResponse({type: messages.loginFailed, detail: detail});
    }

    hookCookieSync(matchCookie) {
        chrome.cookies.onChanged.addListener(changeInfo => {
            const cookie = changeInfo.cookie;

            if (changeInfo.cause === 'explicit' && matchCookie(cookie)) {
                this.syncCookies(false);
            }
        });

        chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
            if (request.type && request.type === messages.requestLogin) {
                this.onRequestLogin(sendResponse);
                return true;
            }
        });
    }

    async onGetTorrentStatuses(request, sendResponse) {
        try {
            const response = await this.performPOST('/api/torrents/', {
                body: JSON.stringify({
                    realm_name: request.realmName,
                    tracker_ids: request.torrentIds,
                    page_size: 1000,
                }),
            });
            sendResponse({
                type: messages.getTorrentStatusesSuccess,
                torrents: response,
            });
        } catch (exception) {
            sendResponse({
                type: messages.getTorrentStatusesError,
                detail: exception.toString(),
            });
        }
    }

    hookTorrentStatuses() {
        chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
            if (request.type && request.type === messages.getTorrentStatuses) {
                this.onGetTorrentStatuses(request, sendResponse);
                return true;
            }
        });
    }
}
