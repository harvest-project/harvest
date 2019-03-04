import {message} from 'antd';
import {ResponseErrorDisplay} from 'home/assets/controls/ResponseErrorDisplay';
import Cookies from 'js-cookie';
import React from 'react';

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

export class APIHelper {
    static _addConfig(input, init) {
        init.headers = init.headers || new Headers();
        init.headers.append('X-CSRFToken', Cookies.get('csrftoken'));
        init.credentials = 'same-origin';

        if (typeof init.jsonBody !== 'undefined') {
            init.body = JSON.stringify(init.jsonBody);
            init.headers.append('Content-Type', 'application/json');
            delete init.jsonBody;
        }

        if (typeof init.queryParams !== 'undefined') {
            input = input + '?' + formatQueryParams(init.queryParams);
            delete init.queryParams;
        }

        return input
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
        input = this._addConfig(input, init);
        return this._wrapResponse(await fetch(input, init));
    }

    static async put(input, init = {}) {
        init.method = 'PUT';
        input = this._addConfig(input, init);
        return this._wrapResponse(await fetch(input, init));
    }

    static async post(input, init = {}) {
        init.method = 'POST';
        input = this._addConfig(input, init);
        return this._wrapResponse(await fetch(input, init));
    }

    static async delete(input, init = {}) {
        init.method = 'DELETE';
        input = this._addConfig(input, init);
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
