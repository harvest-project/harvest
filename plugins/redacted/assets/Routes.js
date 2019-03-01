import {Settings} from 'plugins/redacted/assets/pages/Settings';
import {RedactedUrls} from 'plugins/redacted/assets/RedactedUrls';
import React from 'react';
import {Route} from 'react-router-dom';

export class Routes extends React.Component {
    render() {
        return <>
            <Route path={RedactedUrls.settings} component={Settings}/>
        </>;
    }
}
