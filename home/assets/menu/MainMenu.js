import {Icon, Menu} from 'antd';
import {HomeUrls} from 'home/assets/HomeUrls';
import {SettingsMenu} from 'home/assets/menu/SettingsMenu';
import React from 'react';
import {Link, withRouter} from 'react-router-dom';
import {TorrentsUrls} from 'torrents/assets/TorrentsUrls';
import {MonitoringUrls} from 'monitoring/assets/MonitoringUrls';
import {UploadStudioUrls} from 'upload_studio/assets/UploadStudioUrls';
import {MenuRegistry} from 'home/assets/PluginRegistry';

const {SubMenu} = Menu;

@withRouter
export class MainMenu extends React.Component {
    constructor(props) {
        super(props);

        this.defaultSelectedKeys = [this.props.location.pathname];
        this.defaultOpenKeys = [];
        for (const pathPiece of this.props.location.pathname.split('/')) {
            if (this.defaultOpenKeys.length === 0) {
                this.defaultOpenKeys.push(pathPiece);
            } else {
                const lastPiece = this.defaultOpenKeys[this.defaultOpenKeys.length - 1];
                this.defaultOpenKeys.push(lastPiece + '/' + pathPiece);
            }
        }
    }

    render() {
        return <Menu
            mode="inline"
            theme="dark"
            defaultSelectedKeys={this.defaultSelectedKeys}
            defaultOpenKeys={['/settings']}
        >
            <Menu.Item key={HomeUrls.dashboard}>
                <Link to={HomeUrls.dashboard}>
                    <Icon type="home"/>
                    <span>Dashboard</span>
                </Link>
            </Menu.Item>

            <Menu.Item key={TorrentsUrls.torrents}>
                <Link to={TorrentsUrls.torrents}>
                    <Icon type="bars"/>
                    <span>Torrents</span>
                </Link>
            </Menu.Item>

            <Menu.Item key={MonitoringUrls.monitoring}>
                <Link to={MonitoringUrls.monitoring}>
                    <Icon type="safety"/>
                    <span>Monitoring</span>
                </Link>
            </Menu.Item>

            <Menu.Item key={UploadStudioUrls.projects}>
                <Link to={UploadStudioUrls.projects}>
                    <Icon type="upload"/>
                    <span>Upload</span>
                </Link>
            </Menu.Item>

            <SettingsMenu/>

            {MenuRegistry.mainMenuItems}
        </Menu>;
    }
}
