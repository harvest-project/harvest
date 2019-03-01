import {Button, Table} from 'antd';
import {APIHelper} from 'home/assets/api/APIHelper';
import {Timer} from 'home/assets/controls/Timer';
import {UIContext} from 'home/assets/contexts';
import React from 'react';
import {AddClient} from 'torrents/assets/components/AddClient';
import {TorrentsAPI} from 'torrents/assets/TorrentsAPI';

export class AlcazarInstances extends React.Component {
    static contextType = UIContext;
    static columns = [
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
            dataIndex: 'num_torrents',
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
            </p>;
        } else if (client.type === 'managed_libtorrent') {
            return <p>
                State Path: {client.state_path}<br/>
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
                expandedRowRender={this.expandedRowRender}
            />
        </div>;
    }
}
