import {Menu} from 'antd';
import {MenuRegistry, RouteRegistry, TrackerRegistry} from 'home/assets/PluginRegistry';
import {BibliotikUrls} from 'plugins/bibliotik/assets/BibliotikUrls';
import bibliotik from 'plugins/bibliotik/assets/images/bibliotik.png';
import {Routes} from 'plugins/bibliotik/assets/Routes';
import React from 'react';
import {Link} from 'react-router-dom';
import {MetadataColumnDisplay} from 'plugins/bibliotik/assets/controls/MetadataColumnDisplay';

class BibliotikTracker {
    static trackerName = 'bibliotik';
    static displayName = 'Bibliotik.me Tracker';
    static metadataColumnRenderer = MetadataColumnDisplay;

    static getTorrentUrl(torrentInfo) {
        return `https://bibliotik.me/torrents/${torrentInfo.tracker_id}`;
    }
}

TrackerRegistry.register(new BibliotikTracker());
RouteRegistry.registerPageRoutesComponent(Routes);

MenuRegistry.registerSettingsMenuItem((
    <Menu.Item key={BibliotikUrls.settings}>
        <Link to={BibliotikUrls.settings}>
            <img src={bibliotik} style={{width: 14, height: 14, marginRight: 10, verticalAlign: -1.75}}/>
            <span>Bibliotik.me</span>
        </Link>
    </Menu.Item>
));
