import {Button, Drawer, Icon, Progress, Table} from 'antd';
import {APIHelper} from 'home/assets/api/APIHelper';
import {UIContext} from 'home/assets/contexts';
import {DivRow} from 'home/assets/controls/DivRow';
import {Timer} from 'home/assets/controls/Timer';
import prettysize from 'prettysize';
import React from 'react';
import {TorrentDetailsDisplay} from 'torrents/assets/components/TorrentDetailsDisplay';
import {TorrentsAPI} from 'torrents/assets/TorrentsAPI';

function renderIcon(data, record, index) {
    if (record.error) {
        return <Icon type="close-circle" style={{color: 'red', fontSize: 18}}/>;
    }
    if (record.progress < 1) {
        return <Icon type="download" style={{color: '#1890ff', fontSize: 18}}/>;
    }
    return <Icon type="upload" style={{color: '#52c41a', fontSize: 18}}/>;
}


function getRowClassName(record, index) {
    if (record.error) {
        return 'table-row-error';
    }
    return null;
}


const columns = [
    {
        title: 'ID',
        dataIndex: 'id',
    },
    {
        key: 'icon',
        title: '',
        render: renderIcon,
    },
    {
        title: 'Name',
        dataIndex: 'name',
    },
    {
        title: 'Size',
        dataIndex: 'size',
        render: (data, record, index) => prettysize(data),
    },
    {
        title: 'Progress',
        dataIndex: 'progress',
        render: (data, record, index) => <Progress percent={Math.floor(data * 100)} size="small"/>,
        width: 140,
    },
    {
        title: 'Error',
        dataIndex: 'error',
    },
];

export class Torrents extends React.Component {
    static contextType = UIContext;

    constructor(props) {
        super(props);

        this.state = {
            torrents: [],
            selectedTorrent: null,
        };

        this.onRow = record => ({
            onClick: () => this.selectRow(record),
        });
    }

    componentDidMount() {
        this.context.trackLoadingAsync(async () => this.refreshInstances());
    }

    async refreshInstances() {
        let data;
        try {
            data = await TorrentsAPI.getTorrents();
        } catch (response) {
            await APIHelper.showResponseError(response, 'Failed to load torrents');
            return;
        }
        this.setState({
            torrents: data.torrents,
        });

        if (this.state.selectedTorrent) {
            let selectedTorrent = null;
            for (const torrent of data.torrents) {
                if (torrent.id === this.state.selectedTorrent.id) {
                    selectedTorrent = torrent;
                    break;
                }
            }
            this.setState({
                selectedTorrent: selectedTorrent,
            });
        }
    }

    selectRow(record) {
        this.setState({
            selectedTorrent: record,
        });
    }

    async deleteSelectedTorrent() {
        try {
            await TorrentsAPI.deleteTorrentById(this.state.selectedTorrent.id);
        } catch (response) {
            await APIHelper.showResponseError(response, 'Failed to load torrents');
            return;
        }
        this.setState({
            selectedTorrent: null,
        });
    }

    renderDrawer() {
        const st = this.state.selectedTorrent;
        return <Drawer
            title={st ? st.name : ''}
            width={460}
            placement="right"
            closable={false}
            onClose={() => this.setState({selectedTorrent: null})}
            visible={!!this.state.selectedTorrent}
        >
            {st ? <TorrentDetailsDisplay
                torrent={st}
                onDelete={() => this.deleteSelectedTorrent()}
            /> : null}
        </Drawer>;
    }

    render() {
        return <div>
            <Timer interval={3000} onInterval={() => this.refreshInstances()}/>

            <DivRow>
                <Button type="primary">Add Torrent</Button>
            </DivRow>

            <Table
                size="small"
                dataSource={this.state.torrents}
                columns={columns}
                rowKey="id"
                onRow={this.onRow}
                rowClassName={getRowClassName}
            />

            {this.renderDrawer()}
        </div>;
    }
}
