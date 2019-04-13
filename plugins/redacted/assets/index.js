import {Menu} from 'antd';
import {MenuRegistry, RouteRegistry, TrackerRegistry} from 'home/assets/PluginRegistry';
import redacted from 'plugins/redacted/assets/images/redacted.png';
import {RedactedUrls} from 'plugins/redacted/assets/RedactedUrls';
import React from 'react';
import {Link, Route} from 'react-router-dom';
import {MetadataColumnDisplay} from 'plugins/redacted/assets/controls/MetadataColumnDisplay';
import {Settings} from 'plugins/redacted/assets/pages/Settings';

class RedactedTracker {
    trackerName = 'redacted';
    displayName = 'Redacted.ch Tracker';
    metadataColumnRenderer = MetadataColumnDisplay;

    getTorrentUrl(torrentInfo) {
        return `https://redacted.ch/torrents.php?torrentid=${torrentInfo.tracker_id}`;
    }
}

TrackerRegistry.register(new RedactedTracker());
RouteRegistry.addPageRoute(<Route key={RedactedUrls.settings} path={RedactedUrls.settings} component={Settings}/>);

MenuRegistry.addSettingsMenuItem((
    <Menu.Item key={RedactedUrls.settings}>
        <Link to={RedactedUrls.settings}>
            <img src={redacted} style={{width: 14, height: 14, marginRight: 10, verticalAlign: -1.75}}/>
            <span>Redacted.ch</span>
        </Link>
    </Menu.Item>
));
