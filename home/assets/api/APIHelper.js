import {message} from 'antd';
import {ResponseErrorDisplay} from 'home/assets/controls/ResponseErrorDisplay';
import Cookies from 'js-cookie';
import React from 'react';

export class APIHelper {
    static _addConfig(init) {
        init.headers = init.headers || new Headers();
        init.headers.append('X-CSRFToken', Cookies.get('csrftoken'));
        init.credentials = 'same-origin';

        if (typeof init.jsonBody !== 'undefined') {
            init.body = JSON.stringify(init.jsonBody);
            init.headers.append('Content-Type', 'application/json');
            delete init.jsonBody;
        }
    }

    static _wrapResponse(response) {
        if (!response.ok) {
            throw response;
        }
        if (response.status === 204) { // No Content
            return null;
        }
        return response.json();
    }

    static async get(input, init = {}) {
        init.method = 'GET';
        return this._wrapResponse(await fetch(input, init));
    }

    static async put(input, init = {}) {
        init.method = 'PUT';
        this._addConfig(init);
        return this._wrapResponse(await fetch(input, init));
    }

    static async post(input, init = {}) {
        init.method = 'POST';
        this._addConfig(init);
        return this._wrapResponse(await fetch(input, init));
    }

    static async delete(input, init = {}) {
        init.method = 'DELETE';
        this._addConfig(init);
        return this._wrapResponse(await fetch(input, init));
    }

    static async showResponseError(response, additionalMessage) {
        let responseJson = null;
        try {
            responseJson = await response.json();
        } catch {
        }

        message.error(<ResponseErrorDisplay
            response={response}
            additionalMessage={additionalMessage}
            responseJson={responseJson}
        />);
    }
}
