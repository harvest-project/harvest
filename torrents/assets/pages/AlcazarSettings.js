import {Tabs} from 'antd';
import React from 'react';
import {AlcazarConfig} from 'torrents/assets/components/AlcazarConfig';
import {AlcazarInstances} from 'torrents/assets/components/AlcazarInstances';


export class AlcazarSettings extends React.Component {
    render() {
        return <Tabs>
            <Tabs.TabPane tab="Config" key="config"><AlcazarConfig/></Tabs.TabPane>
            <Tabs.TabPane tab="Instances" key="instances"><AlcazarInstances/></Tabs.TabPane>
        </Tabs>;
    }
}
