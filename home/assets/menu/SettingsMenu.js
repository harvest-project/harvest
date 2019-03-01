import {Icon, Menu} from 'antd';
import {plugins} from 'home/assets/PluginRegistry';
import React from 'react';
import {Link} from 'react-router-dom';
import {SettingsUrls} from 'settings/assets/SettingsUrls';
import {TorrentsUrls} from 'torrents/assets/TorrentsUrls';

const {SubMenu} = Menu;

export class SettingsMenu extends React.Component {
    constructor(props) {
        super(props);

        this.pluginItems = [];
        for (const plugin of plugins) {
            this.pluginItems = this.pluginItems.concat(plugin.settingsMenuItems || []);
        }
    }

    render() {
        return <SubMenu
            key="/settings"
            title={<span><Icon type="setting"/><span>Settings</span></span>}
            {...this.props}
        >
            <Menu.Item key={SettingsUrls.settings}>
                <Link to={SettingsUrls.settings}>
                    <Icon type="user"/>
                    <span>Harvest</span>
                </Link>
            </Menu.Item>

            <Menu.Item key={TorrentsUrls.alcazarSettings}>
                <Link to={TorrentsUrls.alcazarSettings}>
                    <Icon type="download"/>
                    <span>Alcazar</span>
                </Link>
            </Menu.Item>

            {this.pluginItems}
        </SubMenu>;
    }
}
