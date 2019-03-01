import {Menu} from 'antd';
import {registerPlugin} from 'home/assets/PluginRegistry';
import {RedactedUrls} from 'plugins/redacted/assets/RedactedUrls';
import {Routes} from 'plugins/redacted/assets/Routes';
import redacted from 'plugins/redacted/assets/images/redacted.png';
import React from 'react';
import {Link} from 'react-router-dom';

class RedactedCh {
    static pluginName = 'Redacted.ch Plugin';

    static mainMenuItems = [
        () => (
            /*<ListItem button>
                <ListItemIcon><EditIcon/></ListItemIcon>
                <ListItemText>Redacted Plugin</ListItemText>
            </ListItem>*/
            null
        ),
    ];

    static settingsMenuItems = [
        <Menu.Item key={RedactedUrls.settings}>
            <Link to={RedactedUrls.settings}>
                <img src={redacted} style={{width: 14, height: 14, marginRight: 10, verticalAlign: -1.75}}/>
                <span>Settings</span>
            </Link>
        </Menu.Item>,
    ];

    static routes = Routes;
}

registerPlugin(RedactedCh);
