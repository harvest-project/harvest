import {Alert, Button, Drawer, Dropdown, Icon, Menu, Progress, Select, Table} from 'antd';
import {APIHelper} from 'home/assets/api/APIHelper';
import {HarvestContext} from 'home/assets/context';
import {DivRow} from 'home/assets/controls/DivRow';
import {Timer} from 'home/assets/controls/Timer';
import {formatBytes} from 'home/utils';
import React from 'react';
import {AddTorrentFromFile} from 'torrents/assets/components/AddTorrentFromFile';
import {AddTorrentFromTracker} from 'torrents/assets/components/AddTorrentFromTracker';
import {TorrentDetailsDisplay} from 'torrents/assets/components/TorrentDetailsDisplay';
import {TorrentsAPI} from 'torrents/assets/TorrentsAPI';
import {TorrentStatus} from 'torrents/assets/utils';

const iconError = <Icon type="close-circle" style={{color: 'red', fontSize: 18}}/>;
const iconDownloading = <Icon type="download" style={{color: '#1890ff', fontSize: 18}}/>;
const iconSeeding = <Icon type="upload" style={{color: '#52c41a', fontSize: 18}}/>;
const iconWaiting = <Icon type="clock-circle" style={{color: '#cccccc', fontSize: 18}}/>;
const iconStopped = <Icon type="pause-circle" style={{color: '#cccccc', fontSize: 18}}/>;
const iconUnknown = <Icon type="question-circle" style={{color: 'red', fontSize: 18}}/>;

const FILTER_ALL = 'all';
const FILTER_ACTIVE = 'active';
const FILTER_DOWNLOADING = 'downloading';
const FILTER_ERRORS = 'errors';

const MAX_TORRENTS = 200;
const TORRENTS_PER_PAGE = 40;

function renderIcon(data, record, index) {
    if (record.error || record.tracker_error) {
        return iconError;
    }
    if (record.status === TorrentStatus.CHECK_WAITING || record.status === TorrentStatus.CHECKING) {
        return iconWaiting;
    }
    if (record.status === TorrentStatus.DOWNLOADING) {
        return iconDownloading;
    }
    if (record.status === TorrentStatus.SEEDING) {
        return iconSeeding;
    }
    if (record.status === TorrentStatus.STOPPED) {
        return iconStopped;
    }
    return iconUnknown;
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
        render: (data, record, index) => formatBytes(data),
    },
    {
        title: 'Progress',
        dataIndex: 'progress',
        render: (data, record, index) => <Progress percent={Math.floor(data * 100)} size="small"/>,
        width: 140,
    },
    {
        key: 'error',
        title: 'Error',
        render: (data, record, index) => <span>{record.error || record.tracker_error}</span>,
    },
];

export class Torrents extends React.Component {
    static contextType = HarvestContext;

    constructor(props) {
        super(props);

        this.state = {
            torrentsFilter: FILTER_ALL,
            torrentsRealmId: null,
            torrents: [],
            selectedTorrent: null,
            addFromFile: false,
            addFromTracker: false,
        };

        this.onRow = record => ({
            onClick: () => this.selectRow(record),
        });

        this.queryIndex = 0; // Used to avoid duplicate / out-of-order AJAX queries
    }

    componentDidMount() {
        this.context.trackLoadingAsync(async () => this.refreshTorrents());
    }

    async refreshTorrents() {
        const queryIndex = ++this.queryIndex;
        let data;

        try {
            data = await TorrentsAPI.getTorrents(
                this.state.torrentsFilter,
                this.state.torrentsRealmId,
                MAX_TORRENTS,
            );
        } catch (response) {
            await APIHelper.showResponseError(response, 'Failed to load torrents');
            return;
        }

        if (this.queryIndex !== queryIndex) {
            console.log('Cancelling obsolete request.');
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

    setFilter(filter) {
        this.setState({
            torrentsFilter: filter,
        }, () => {
            this.context.trackLoadingAsync(async () => this.refreshTorrents());
        });
    }

    setRealm(realmId) {
        this.setState({
            torrentsRealmId: realmId,
        }, () => {
            this.context.trackLoadingAsync(async () => this.refreshTorrents());
        });
    }

    getFilterButtonType(filter) {
        return this.state.torrentsFilter === filter ? 'primary' : 'default';
    }

    renderDrawer() {
        const st = this.state.selectedTorrent;
        return <Drawer
            title={st ? st.name : ''}
            width={440}
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
            <Timer interval={3000} onInterval={() => this.refreshTorrents()}/>

            <DivRow>
                <Dropdown overlay={<Menu>
                    <Menu.Item key="file" onClick={() => this.setState({addFromFile: true})}>
                        From File
                    </Menu.Item>
                    <Menu.Item key="tracker" onClick={() => this.setState({addFromTracker: true})}>
                        From Tracker
                    </Menu.Item>
                </Menu>}>
                    <Button htmlType="button" type="primary" icon="plus">
                        Add Torrent <Icon type="down"/>
                    </Button>
                </Dropdown>

                {' '}Filter:{' '}
                <Button.Group>
                    <Button htmlType="button" type={this.getFilterButtonType(FILTER_ALL)}
                            onClick={() => this.setFilter(FILTER_ALL)}>
                        All
                    </Button>
                    <Button htmlType="button" type={this.getFilterButtonType(FILTER_ACTIVE)}
                            onClick={() => this.setFilter(FILTER_ACTIVE)}>
                        Active
                    </Button>
                    <Button htmlType="button" type={this.getFilterButtonType(FILTER_DOWNLOADING)}
                            onClick={() => this.setFilter(FILTER_DOWNLOADING)}>
                        Downloading
                    </Button>
                    <Button htmlType="button" type={this.getFilterButtonType(FILTER_ERRORS)}
                            onClick={() => this.setFilter(FILTER_ERRORS)}>
                        Errors
                    </Button>
                </Button.Group>

                {' '}Realm:{' '}
                <Select value={this.state.torrentsRealmId}
                        onChange={value => this.setRealm(value)}
                        style={{width: 120}}>
                    <Select.Option key="all" value={null}>
                        All
                    </Select.Option>

                    {this.context.realms.map(realm => (
                        <Select.Option key={realm.id} value={realm.id}>
                            {realm.name}
                        </Select.Option>
                    ))}
                </Select>
            </DivRow>

            {this.state.torrents.length === MAX_TORRENTS ? <DivRow>
                <Alert type="warning" message={`Too many torrents matched. Showing only ${MAX_TORRENTS}.`}/>
            </DivRow> : null}

            <Table
                size="small"
                dataSource={this.state.torrents}
                columns={columns}
                rowKey="id"
                onRow={this.onRow}
                rowClassName={getRowClassName}
                pagination={{
                    defaultPageSize: TORRENTS_PER_PAGE,
                }}
            />

            <AddTorrentFromFile visible={this.state.addFromFile}
                                onHide={() => this.setState({addFromFile: false})}/>
            <AddTorrentFromTracker visible={this.state.addFromTracker}
                                   onHide={() => this.setState({addFromTracker: false})}/>

            {this.renderDrawer()}
        </div>;
    }
}
