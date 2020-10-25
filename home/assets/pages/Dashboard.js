import {Card, Col, Progress, Row, Statistic} from 'antd';
import {APIHelper} from 'home/assets/api/APIHelper';
import {HomeAPI} from 'home/assets/api/HomeAPI';
import {HarvestContext} from 'home/assets/context';
import {DivRow} from 'home/assets/controls/DivRow';
import {Timer} from 'home/assets/controls/Timer';
import {formatBytes} from 'home/assets/utils';
import {observer} from 'mobx-react';
import React from 'react';
import styles from './Dashboard.less';
import {ComponentStatuses} from 'monitoring/assets/components/ComponentStatuses.js';

@observer
export class Dashboard extends React.Component {
    static contextType = HarvestContext;

    constructor(props) {
        super(props);

        this.state = {
            data: null,
        };
    }

    componentDidMount() {
        this.context.trackLoadingAsync(async () => this.refreshData());
    }

    async refreshData() {
        let data;
        try {
            data = await HomeAPI.getDashboardData();
        } catch (response) {
            await APIHelper.showResponseError(response, 'Failed to load data');
            return;
        }
        this.setState({
            data: data,
        });
    }

    render() {
        return <div>
            <Timer interval={5000} onInterval={() => this.refreshData()}/>

            <DivRow>
                <h2>Welcome to Harvest, {this.context.user.full_name}.</h2>
            </DivRow>

            <Row type="flex" gutter={16} className={styles['dashboard-row']}>
                {this.state.data ? this.state.data.disk_usage.map((disk_usage, i) => (
                    <Col key={i} xs={12} sm={8} lg={6} xl={4}>
                        <Card
                            size="small"
                            style={{textAlign: 'center'}}
                            title={`Usage on ${disk_usage.mount}`}
                        >
                            <Progress
                                type="circle"
                                percent={Math.round((disk_usage.total - disk_usage.free) / disk_usage.total * 100)}
                                width={100}
                            />
                        </Card>
                    </Col>
                )) : null}

                {this.state.data ? this.state.data.realm_torrent_counts.map((realm_count, i) => (
                    <Col key={i} xs={12} sm={8} lg={6} xl={4}>
                        <Card size="small" style={{textAlign: 'center'}}
                              title={`${this.context.getRealmById(realm_count.realm).name} stats`}>
                            <Statistic
                                title="Torrents"
                                value={realm_count.torrent_count}
                            />
                            <Statistic
                                title="Size"
                                value={formatBytes(realm_count.torrent_size)}
                            />
                        </Card>
                    </Col>
                )) : null}
            </Row>

            <Row type="flex" gutter={16} className={styles['dashboard-row']}>
                <Col xs={24} sm={24} lg={24} xl={24}>
                    <ComponentStatuses/>
                </Col>
            </Row>
        </div>;
    }
}
