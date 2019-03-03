import {Tabs} from 'antd';
import React from 'react';
import {AlcazarClientSettings} from 'settings/assets/components/AlcazarClientSettings';
import {APISettings} from 'settings/assets/components/APISettings';
import {DownloadLocationsSettings} from 'settings/assets/components/DownloadLocationsSettings';

export class Settings extends React.Component {

    render() {
        return <Tabs>
            <Tabs.TabPane tab="Alcazar Client" key="alcazar_client">
                <AlcazarClientSettings/>
            </Tabs.TabPane>
            <Tabs.TabPane tab="API" key="api">
                <APISettings/>
            </Tabs.TabPane>
            <Tabs.TabPane tab="Download Locations" key="download_location">
                <DownloadLocationsSettings/>
            </Tabs.TabPane>
        </Tabs>;
    }
}
