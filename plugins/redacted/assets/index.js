import {Menu} from 'antd';
import {registerPlugin} from 'home/assets/PluginRegistry';
import redacted from 'plugins/redacted/assets/images/redacted.png';
import {RedactedUrls} from 'plugins/redacted/assets/RedactedUrls';
import {Routes} from 'plugins/redacted/assets/Routes';
import React from 'react';
import {Link} from 'react-router-dom';
import {MetadataColumnDisplay} from "./controls/MetadataColumnDisplay";

class RedactedPlugin {
    static pluginName = 'redacted';
    static displayName = 'Redacted.ch Plugin';

    static mainMenuItems = [];

    static settingsMenuItems = [
        <Menu.Item key={RedactedUrls.settings}>
            <Link to={RedactedUrls.settings}>
                <img src={redacted} style={{width: 14, height: 14, marginRight: 10, verticalAlign: -1.75}}/>
                <span>Redacted.ch</span>
            </Link>
        </Menu.Item>,
    ];

    static routes = Routes;

    static metadataColumnRenderer = MetadataColumnDisplay;
}

registerPlugin(RedactedPlugin);
