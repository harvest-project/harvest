import {Tabs} from 'antd';
import React from 'react';
import {AlcazarClientSettings} from 'settings/assets/pages/AlcazarClientSettings';
import {APISettings} from 'settings/assets/pages/APISettings';

export class Settings extends React.Component {

    render() {
        return <Tabs>
            <Tabs.TabPane tab="Alcazar Client" key="alcazar_client">
                <AlcazarClientSettings/>
            </Tabs.TabPane>
            <Tabs.TabPane tab="API" key="api">
                <APISettings/>
            </Tabs.TabPane>
        </Tabs>;
    }
}
