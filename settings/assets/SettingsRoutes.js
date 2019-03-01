import React from 'react';
import {Route} from 'react-router-dom';
import {Settings} from 'settings/assets/pages/Settings';
import {SettingsUrls} from 'settings/assets/SettingsUrls';

export class SettingsRoutes extends React.Component {
    render() {
        return <div>
            <Route path={SettingsUrls.settings} component={Settings}/>
        </div>
    }
}
