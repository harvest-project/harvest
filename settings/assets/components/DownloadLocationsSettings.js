import {Button, message, Modal, Popconfirm, Table} from 'antd';
import {APIHelper} from 'home/assets/api/APIHelper';
import {HarvestContext} from 'home/assets/context';
import {DivRow} from 'home/assets/controls/DivRow';
import {observer} from 'mobx-react';
import React from 'react';
import {DownloadLocationPatternInput} from 'torrents/assets/controls/DownloadLocationPatternInput';
import {TorrentsAPI} from 'torrents/assets/TorrentsAPI';

@observer
export class DownloadLocationsSettings extends React.Component {
    static contextType = HarvestContext;

    constructor(props) {
        super(props);

        this.columns = [
            {
                title: 'ID',
                dataIndex: 'id',
                width: 80,
            },
            {
                dataIndex: 'pattern',
            },
            {
                key: 'actions',
                title: 'Actions',
                width: 80,
                render: (text, record) => (
                    <div>
                        <Popconfirm title="Are you sure?" onConfirm={() => this.deleteLocation(record.id)}>
                            <a>Delete</a>
                        </Popconfirm>
                    </div>
                ),
            },
        ];

        this.state = {
            addToRealm: null,
            addToTracker: null,
            addPattern: '',
        }
    }

    getRealmLocations(realm) {
        const result = [];
        for (const location of this.context.downloadLocations) {
            if (location.realm === realm.id) {
                result.push(location);
            }
        }
        return result;
    }

    async deleteLocation(locationId) {
        try {
            await TorrentsAPI.deleteDownloadLocation(locationId);
            this.context.downloadLocations = await TorrentsAPI.getDownloadLocations();
        } catch (response) {
            await APIHelper.showResponseError(response, 'Error deleting location');
        }
    }

    async addLocation() {
        if (!this.state.addToRealm) {
            message.error('Please select a realm.');
            return;
        }
        if (!this.state.addPattern) {
            message.error('Please enter a pattern.');
            return;
        }

        try {
            await TorrentsAPI.addDownloadLocation(
                this.state.addToRealm.id,
                this.state.addPattern,
            );
            this.context.downloadLocations = await TorrentsAPI.getDownloadLocations();
        } catch (response) {
            await APIHelper.showResponseError(response, 'Error adding location');
            return;
        }

        this.setState({
            addToRealm: null,
            addPattern: '',
        });
    }

    addToRealm(realm) {
        this.setState({
            addToRealm: realm,
            addToTracker: this.context.getTrackerByName(realm.name),
        });
    }

    render() {
        return <div>
            <h1>Download Locations</h1>

            {this.context.realms.map(realm => <DivRow size="medium" key={realm.id}>
                <h2>
                    {realm.name}{' '}
                    <Button htmlType="button" icon="plus" size="small"
                            onClick={() => this.addToRealm(realm)}/>
                </h2>
                <Table
                    size="small"
                    columns={this.columns}
                    dataSource={this.getRealmLocations(realm)}
                    pagination={false}
                    rowKey={i => i.id}
                />
            </DivRow>)}

            <Modal
                visible={!!this.state.addToRealm}
                title={`Add location to ${this.state.addToRealm ? this.state.addToRealm.name : ''}`}
                onOk={() => this.addLocation()}
                onCancel={() => this.setState({addToRealm: null})}
            >
                <DownloadLocationPatternInput
                    tracker={this.state.addToTracker}
                    value={this.state.addPattern}
                    onChange={value => this.setState({addPattern: value})}
                />
            </Modal>
        </div>;
    }
}
