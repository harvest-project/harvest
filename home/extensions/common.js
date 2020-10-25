import Noty from 'noty';

export const messages = {
    requestLogin: 'requestLogin',
    getTorrentStatuses: 'getTorrentStatuses',
    addTorrent: 'addTorrent',
    getUploadStudioProjects: 'getUploadStudioProjects',
    getDownloadTorrentUrl: 'getDownloadTorrentUrl',
};

function formatQueryParams(queryParams) {
    const items = [];
    for (const [key, value] of Object.entries(queryParams)) {
        if (typeof value === 'undefined' || value === null) {
            continue;
        }
        items.push(encodeURIComponent(key) + '=' + encodeURIComponent(value));
    }
    return items.join('&');
}

export function sendChromeMessage(request) {
    return new Promise((resolve, reject) => {
        chrome.runtime.sendMessage(
            request,
            response => {
                if (typeof response === 'undefined') {
                    reject(undefined);
                } else if (response.success) {
                    resolve(response);
                } else {
                    reject(`Background page handler threw exception: ${response.detail}`);
                }
            },
        );
    });
}

export function hookChromeMessage(type, handler) {
    const asyncHandler = async (request, sendResponse) => {
        try {
            const response = await handler(request);
            response.type = type;
            response.success = true;
            sendResponse(response);
        } catch (exception) {
            let message = JSON.stringify(exception);
            if (exception instanceof Response) {
                try {
                    const json = await exception.json();
                    if (json.detail) {
                        message = `Server returned error ${json.detail}`;
                    } else {
                        message = `Server returned error code ${response.status} ${response.statusCode}`;
                    }
                } catch {
                }
            }

            console.error('Error processing content script message', request, exception);
            sendResponse({
                type: type,
                success: false,
                detail: message,
            });
        }
    };

    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
        if (request.type && request.type === type) {
            asyncHandler(request, sendResponse);
            return true;
        }
    });
}

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

    async fetch(endpoint, options = {}) {
        const {url, token} = await this.fetchConfig();
        options.headers = options.headers || {};
        options.headers['Authorization'] = 'Token ' + token;
        const resp = await fetch(url + endpoint, options);
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
                async ({url, token, ...params}) => {
                    if (!allowEmpty && (!url || !token)) {
                        reject('Please configure both URL and token.');
                    }
                    resolve({url, token, ...params});
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

    async testConnection(syncCookies = false) {
        await this.ping();

        if (syncCookies) {
            try {
                await this.syncCookies();
            } catch (exception) {
                throw `Connection successful, but unable to sync cookies: ${exception}`;
            }
            return 'Connection successful, cookies are synced.';
        } else {
            return 'Connection successful.';
        }
    }

    async onRequestLogin(request, sendResponse) {
        const {autoLogin} = await this.fetchConfig();
        if (!autoLogin) {
            throw 'disabled';
        } else if (await this.syncCookies()) {
            return {};
        } else {
            throw 'No working cookies received from server.';
        }
    }

    hookCookieSync(matchCookie) {
        chrome.cookies.onChanged.addListener(changeInfo => {
            const cookie = changeInfo.cookie;

            if (changeInfo.cause === 'explicit' && matchCookie(cookie)) {
                this.syncCookies(false);
            }
        });
        hookChromeMessage(messages.requestLogin, this.onRequestLogin.bind(this));
    }

    async onGetTorrentStatuses(request) {
        const response = await this.performPOST('/api/torrents/', {
            body: JSON.stringify({
                realm_name: request.realmName,
                tracker_ids: request.torrentIds,
                page_size: 1000,
                serialize_metadata: !!request.serializeMetadata,
            }),
        });
        return {
            torrents: response,
        };
    }

    async onAddTorrent(request) {
        return await this.performPOST('/api/torrents/add-torrent-from-tracker', {
            body: JSON.stringify({
                tracker_name: request.trackerName,
                tracker_id: request.trackerId,
                download_path: request.downloadPath,
            }),
        });
    }

    async onGetUploadStudioProjects(request) {
        return await this.performGET('/api/upload-studio/projects?' + formatQueryParams(request.queryParams || {}));
    }

    async onGetDownloadTorrentUrl(request) {
        const config = await this.fetchConfig();
        return {
            downloadUrl: `${config.url}/api/torrents/by-id/${request.trackerId}/zip`,
        };
    }

    hookTorrents() {
        hookChromeMessage(messages.getTorrentStatuses, this.onGetTorrentStatuses.bind(this));
        hookChromeMessage(messages.addTorrent, this.onAddTorrent.bind(this));
        hookChromeMessage(messages.getUploadStudioProjects, this.onGetUploadStudioProjects.bind(this));
        hookChromeMessage(messages.getDownloadTorrentUrl, this.onGetDownloadTorrentUrl.bind(this));
    }
}
