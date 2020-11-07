import {Timer} from 'home/assets/controls/Timer.js';
import {Table, Tooltip} from 'antd';
import React from 'react';
import {StatusIcon} from 'home/assets/controls/StatusGreenIcon.js';
import {formatDateTimeStringISO} from 'home/assets/utils.js';
import {MonitoringAPI} from 'monitoring/assets/MonitoringAPI.js';
import {APIHelper} from 'home/assets/api/APIHelper.js';
import {InfoCircleOutlined} from '@ant-design/icons';

function getComponentRowClassName(record) {
    if (record.status === 'red') {
        return 'table-row-error';
    } else if (record.status === 'yellow') {
        return 'table-row-warning';
    }
    return null;
}

export class ComponentStatuses extends React.Component {
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
                    {record.traceback ?
                        <Tooltip title={record.traceback} overlayStyle={{width: 400}}>
                            <InfoCircleOutlined/></Tooltip> : null}
                </span>,
            },
        ];

        this.state = {
            loading: false,
            componentStatuses: null,
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

        let componentStatuses;

        try {
            componentStatuses = await MonitoringAPI.getComponentStatuses();
        } catch (response) {
            await APIHelper.showResponseError(response, 'Failed to load torrents');
            return;
        }

        this.setState({
            loading: false,
            componentStatuses: componentStatuses,
        });
    }

    render() {
        return <div>
            <Timer interval={1000} onInterval={() => this.refreshData()}/>

            <h2>Component Statuses</h2>

            <Table
                size="small"
                dataSource={this.state.componentStatuses}
                loading={this.state.loading}
                columns={this.componentColumns}
                rowKey="id"
                onRow={this.onRow}
                rowClassName={getComponentRowClassName}
                pagination={false}
            />
        </div>;
    }
}
