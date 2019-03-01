import React from 'react';
import {Route} from 'react-router-dom';
import {AlcazarSettings} from 'torrents/assets/pages/AlcazarSettings';
import {Torrents} from 'torrents/assets/pages/Torrents';
import {TorrentsUrls} from 'torrents/assets/TorrentsUrls';

export class TorrentsRoutes extends React.Component {
    render() {
        return <div>
            <Route path={TorrentsUrls.torrents} component={Torrents}/>
            <Route path={TorrentsUrls.alcazarSettings} component={AlcazarSettings}/>
        </div>
    }
}
