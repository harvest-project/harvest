import {Menu} from 'antd';
import {MenuRegistry} from 'home/assets/PluginRegistry';
import React from 'react';
import {Link} from 'react-router-dom';
import {SettingsUrls} from 'settings/assets/SettingsUrls';
import {TorrentsUrls} from 'torrents/assets/TorrentsUrls';
import {DownloadOutlined, SettingOutlined, UserOutlined} from '@ant-design/icons';

const {SubMenu} = Menu;

export class SettingsMenu extends React.Component {
    render() {
        return <SubMenu
            key="/settings"
            title={<span><SettingOutlined/><span>Settings</span></span>}
            {...this.props}
        >
            <Menu.Item key={SettingsUrls.settings}>
                <Link to={SettingsUrls.settings}>
                    <UserOutlined/>
                    <span>Harvest</span>
                </Link>
            </Menu.Item>

            <Menu.Item key={TorrentsUrls.alcazarSettings}>
                <Link to={TorrentsUrls.alcazarSettings}>
                    <DownloadOutlined/>
                    <span>Alcazar</span>
                </Link>
            </Menu.Item>

            {MenuRegistry.settingsMenuItems}
        </SubMenu>;
    }
}
