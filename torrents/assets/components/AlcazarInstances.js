import {Button, Icon, Table} from 'antd';
import {APIHelper} from 'home/assets/api/APIHelper';
import {HarvestContext} from 'home/assets/context';
import {Timer} from 'home/assets/controls/Timer';
import {formatBytes, toJSONPretty} from 'home/utils';
import React from 'react';
import {AddClient} from 'torrents/assets/components/AddClient';
import {TorrentsAPI} from 'torrents/assets/TorrentsAPI';

const ICONS = {
    green: <Icon type="check-circle" style={{color: '#52c41a'}}/>,
    yellow: <Icon type="warning" style={{color: '#ddc000'}}/>,
    red: <Icon type="close-circle" style={{color: 'red'}}/>,
};

export class AlcazarInstances extends React.Component {
    static contextType = HarvestContext;
    static columns = [
        {
            key: 'status',
            title: '',
            render: (data, record, index) => ICONS[record.status],
        },
        {
            title: 'Name',
            dataIndex: 'name',
        },
        {
            title: 'Realm',
            dataIndex: 'config.realm',
        },
        {
            title: 'Type',
            dataIndex: 'type',
        },
        {
            title: 'Peer Port',
            dataIndex: 'peer_port',
        },
        {
            title: '# of Torrents',
            dataIndex: 'session_stats.torrent_count',
        },
        {
            key: 'down_speed',
            title: 'Down Speed',
            render: (data, record, index) => <span>
                {formatBytes(record.session_stats ? record.session_stats.download_rate : 0) + '/s'}
            </span>,
        },
        {
            key: 'up_speed',
            title: 'Up Speed',
            render: (data, record, index) => <span>
                {formatBytes(record.session_stats ? record.session_stats.upload_rate : 0) + '/s'}
            </span>,
        },
    ];

    constructor(props) {
        super(props);

        this.state = {
            firstLoad: false,
            clients: [],
            addClientVisible: false,
        }
    }

    componentDidMount() {
        this.context.trackLoadingAsync(async () => this.refreshInstances());
    }

    async refreshInstances() {
        let data;
        try {
            data = await TorrentsAPI.getAlcazarClients();
        } catch (response) {
            await APIHelper.showResponseError(response, 'Failed to load data');
            return;
        }
        this.setState({
            clients: data.clients,
        });
    }

    expandedRowRender(client) {
        if (client.type === 'managed_transmission') {
            return <p>
                PID: {client.pid}<br/>
                RPC Port: {client.rpc_port}<br/>
                RPC Password: {client.config.rpc_password}<br/>
                State Path: {client.state_path}<br/>
                Errors: {toJSONPretty(client.errors)}<br/>
            </p>;
        } else if (client.type === 'remote_transmission') {
            return <p>
                RPC Host: {client.config.rpc_host}<br/>
                RPC Port: {client.config.rpc_port}<br/>
                RPC Username: {client.config.rpc_username}<br/>
                RPC Password: {client.config.rpc_password}<br/>
                Errors: {toJSONPretty(client.errors)}<br/>
            </p>;
        } else if (client.type === 'managed_libtorrent') {
            return <p>
                State Path: {client.state_path}<br/>
                Errors: {toJSONPretty(client.errors)}<br/>
            </p>;
        } else {
            return <p>
                Unknown Client Type: {client.type}<br/>
            </p>;
        }
    }

    displayAddClient(display) {
        this.setState({
            addClientVisible: display,
        });
    }

    render() {
        return <div>
            <Timer interval={1000} onInterval={() => this.refreshInstances()}/>

            <p>
                <Button htmlType="button" type="primary" onClick={() => this.displayAddClient(true)}>
                    Add Client
                </Button>
            </p>

            <AddClient visible={this.state.addClientVisible} onHide={() => this.displayAddClient(false)}/>

            <Table
                dataSource={this.state.clients}
                columns={this.constructor.columns}
                rowKey={i => i.name}
                pagination={false}
                expandedRowRender={this.expandedRowRender}
            />
        </div>;
    }
}
