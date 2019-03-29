import {Icon, Table, Tooltip} from 'antd';
import {APIHelper} from 'home/assets/api/APIHelper';
import {HarvestContext} from 'home/assets/context';
import {Timer} from 'home/assets/controls/Timer';
import React from 'react';
import {MonitoringAPI} from 'monitoring/assets/MonitoringAPI';
import {StatusIcon} from 'home/assets/controls/StatusGreenIcon';
import {formatDateTimeStringISO} from 'home/assets/utils';

function getComponentRowClassName(record) {
    if (record.status === 'red') {
        return 'table-row-error';
    } else if (record.status === 'yellow') {
        return 'table-row-warning';
    }
    return null;
}

function getLogRowClassName(record) {
    if (record.level >= 40) {
        return 'table-row-error';
    } else if (record.level >= 30) {
        return 'table-row-warning';
    } else if (record.level >= 20) {
        return 'table-row-info';
    }
    return null;
}

const levelNames = {
    50: 'critical',
    40: 'error',
    30: 'warning',
    20: 'info',
    10: 'debug',
};

function getLevelName(level) {
    return levelNames[level];
}

export class Monitoring extends React.Component {
    static contextType = HarvestContext;

    constructor(props) {
        super(props);

        this.componentColumns = [
            {
                title: '',
                dataIndex: 'status',
                render: data => <StatusIcon status={data}/>,
                width: 30,
            },
            {
                title: 'Updated',
                dataIndex: 'updated_datetime',
                render: formatDateTimeStringISO,
                width: 150,
            },
            {
                title: 'Name',
                dataIndex: 'name',
                width: 220,
            },
            {
                title: 'Message',
                dataIndex: 'message',
                render: (data, record) => <span>
                    {data}
                    {' '}
                    {record.traceback ? <Tooltip title={record.traceback} overlayStyle={{width: 400}}>
                        <Icon type="info-circle"/></Tooltip> : null}
                </span>,
            },
        ];

        this.logColumns = [
            {
                title: 'Level',
                dataIndex: 'level',
                render: getLevelName,
                width: 70,
            },
            {
                title: 'Created',
                dataIndex: 'created_datetime',
                render: formatDateTimeStringISO,
                width: 150,
            },
            {
                title: 'Message',
                dataIndex: 'message',
                render: (data, record) => <span>
                    {data}
                    {' '}
                    {record.traceback ? <Tooltip title={record.traceback} overlayStyle={{width: 400}}>
                        <Icon type="info-circle"/></Tooltip> : null}
                </span>,
            },
        ];

        this.state = {
            loading: false,
            componentStatuses: null,
            logEntries: null,
        };
    }

    componentDidMount() {
        this.refreshData(true);
    }

    async refreshData(modalLoading = false) {
        if (!modalLoading && this.state.loading) {
            return; // Do not supersede a modal (main) loading request
        }

        this.setState({
            loading: modalLoading,
        });

        let data;

        try {
            data = await MonitoringAPI.getMonitoringData();
        } catch (response) {
            await APIHelper.showResponseError(response, 'Failed to load torrents');
            return;
        }

        this.setState({
            loading: false,
            componentStates: data.component_statuses,
            logEntries: data.log_entries,
        });
    }

    render() {
        return <div>
            <Timer interval={1000} onInterval={() => this.refreshData()}/>

            <h2>Component Statuses</h2>

            <Table
                size="small"
                dataSource={this.state.componentStates}
                loading={this.state.loading}
                columns={this.componentColumns}
                rowKey="id"
                onRow={this.onRow}
                rowClassName={getComponentRowClassName}
                pagination={false}
            />

            <br/>
            <h2>Log Entries</h2>

            <Table
                size="small"
                dataSource={this.state.logEntries}
                loading={this.state.loading}
                columns={this.logColumns}
                rowKey="id"
                onRow={this.onRow}
                rowClassName={getLogRowClassName}
                pagination={false}
            />
        </div>;
    }
}
