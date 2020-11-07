import {Layout} from 'antd';
import {APIHelper} from 'home/assets/api/APIHelper';
import {AuthAPI} from 'home/assets/api/AuthAPI';
import {HarvestContext} from 'home/assets/context';
import {Timer} from 'home/assets/controls/Timer';
import {formatBytes} from 'home/assets/utils';
import React from 'react';
import {TorrentsAPI} from 'torrents/assets/TorrentsAPI';
import styles from './HarvestHeader.less';
import {
    CheckCircleOutlined,
    ClockCircleOutlined,
    CloseCircleOutlined,
    LogoutOutlined,
    WarningOutlined,
} from '@ant-design/icons';

const sizes = {
    small: 8,
    medium: 16,
    large: 24,
};

const _ALCAZAR_DOWN = '__down';

export class HarvestHeader extends React.Component {
    static contextType = HarvestContext;

    constructor(props) {
        super(props);

        this.state = {
            clients: null,
        };
    }

    logout = async () => {
        try {
            await AuthAPI.logout();
        } catch (response) {
            await APIHelper.showResponseError(response);
        }
        this.context.user = null;
    };

    async refreshInstances() {
        let data;
        try {
            data = await TorrentsAPI.getAlcazarClients();
            this.setState({
                clients: data.clients,
            });
        } catch (response) {
            this.setState({
                clients: _ALCAZAR_DOWN,
            });
        }
    }

    renderAlcazarStatus() {
        if (this.state.clients === null) {
            return <span><ClockCircleOutlined/> Loading Alcazar status...</span>;
        } else if (this.state.clients === _ALCAZAR_DOWN) {
            return <span>
                <CloseCircleOutlined style={{color: 'red'}}/>{' '}
                Error connecting to Harvest/Alcazar. Check your setup.
            </span>;
        } else {
            const allGreen = this.state.clients.map(c => c.status === 'green').reduce((a, b) => a && b, true);
            const downRate = this.state.clients
                .map(c => c.session_stats ? c.session_stats.download_rate : 0)
                .reduce((a, b) => a + b, 0);
            const upRate = this.state.clients
                .map(c => c.session_stats ? c.session_stats.upload_rate : 0)
                .reduce((a, b) => a + b, 0);
            return <span>
                {allGreen ?
                    <CheckCircleOutlined style={{color: '#52c41a'}}/> :
                    <WarningOutlined style={{color: '#ddc000'}}/>}
                &nbsp;
                Alcazar is up. Up: {formatBytes(upRate)}/s. Down: {formatBytes(downRate)}/s.
            </span>;
        }
    }

    render() {
        return <Layout.Header className={styles['header-container']}>
            <Timer fireImmediately interval={3000} onInterval={() => this.refreshInstances()}/>

            <div className={styles['header-item']}>
                {this.renderAlcazarStatus()}
            </div>
            <div className={styles['header-spacer']}/>
            <div className={styles['header-button']} onClick={this.logout}>
                <LogoutOutlined/> Logout
            </div>
        </Layout.Header>
    }
}
