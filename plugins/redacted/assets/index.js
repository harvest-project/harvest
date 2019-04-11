import {Menu} from 'antd';
import {MenuRegistry, registerPlugin, RouteRegistry, TrackerRegistry} from 'home/assets/PluginRegistry';
import redacted from 'plugins/redacted/assets/images/redacted.png';
import {RedactedUrls} from 'plugins/redacted/assets/RedactedUrls';
import {Routes} from 'plugins/redacted/assets/Routes';
import React from 'react';
import {Link} from 'react-router-dom';
import {MetadataColumnDisplay} from './controls/MetadataColumnDisplay';

class RedactedTracker {
    static trackerName = 'redacted';
    static displayName = 'Redacted.ch Tracker';
    static metadataColumnRenderer = MetadataColumnDisplay;

    static getTorrentUrl(torrentInfo) {
        return `https://redacted.ch/torrents.php?torrentid=${torrentInfo.tracker_id}`;
    }
}

TrackerRegistry.register(new RedactedTracker());
RouteRegistry.registerPageRoutesComponent(Routes);

MenuRegistry.registerSettingsMenuItem((
    <Menu.Item key={RedactedUrls.settings}>
        <Link to={RedactedUrls.settings}>
            <img src={redacted} style={{width: 14, height: 14, marginRight: 10, verticalAlign: -1.75}}/>
            <span>Redacted.ch</span>
        </Link>
    </Menu.Item>
));
