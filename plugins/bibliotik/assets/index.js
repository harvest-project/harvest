import {Menu} from 'antd';
import {MenuRegistry, RouteRegistry, TrackerRegistry} from 'home/assets/PluginRegistry';
import {BibliotikUrls} from 'plugins/bibliotik/assets/BibliotikUrls';
import bibliotik from 'plugins/bibliotik/assets/images/bibliotik.png';
import React from 'react';
import {Link, Route} from 'react-router-dom';
import {MetadataColumnDisplay} from 'plugins/bibliotik/assets/controls/MetadataColumnDisplay';
import {Settings} from 'plugins/bibliotik/assets/pages/Settings';

class BibliotikTracker {
    trackerName = 'bibliotik';
    displayName = 'Bibliotik.me Tracker';
    metadataColumnRenderer = MetadataColumnDisplay;

    getTorrentUrl(torrentInfo) {
        return `https://bibliotik.me/torrents/${torrentInfo.tracker_id}`;
    }
}

TrackerRegistry.register(new BibliotikTracker());
RouteRegistry.addPageRoute(<Route key={BibliotikUrls.settings} path={BibliotikUrls.settings} component={Settings}/>);

MenuRegistry.addSettingsMenuItem((
    <Menu.Item key={BibliotikUrls.settings}>
        <Link to={BibliotikUrls.settings}>
            <img src={bibliotik} style={{width: 14, height: 14, marginRight: 10, verticalAlign: -1.75}}/>
            <span>Bibliotik.me</span>
        </Link>
    </Menu.Item>
));
