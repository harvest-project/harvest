import {Form, message, Modal, Select, Spin} from 'antd';
import {APIHelper} from 'home/assets/api/APIHelper';
import React from 'react';
import {TorrentsAPI} from 'torrents/assets/TorrentsAPI';
import {TrackersAPI} from 'trackers/assets/TrackersAPI';

export class AddClient extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            isSaving: false,
            selectedRealm: null,
            selectedInstanceType: null,
            addClientInstanceType: 'managed_libtorrent',
            trackers: [],
        }
    }

    async fetchTrackers() {
        const response = await TrackersAPI.getTrackers();
        this.setState({
            trackers: response.trackers,
        });
    }

    componentDidMount() {
        this.fetchTrackers();
    }

    async addClient() {
        if (!this.state.selectedRealm || !this.state.selectedInstanceType) {
            message.error('Please select a realm and an instance type.');
            return;
        }

        this.setState({isSaving: true});
        try {
            await TorrentsAPI.addAlcazarClient(
                this.state.selectedRealm,
                this.state.selectedInstanceType,
            );
        } catch (response) {
            await APIHelper.showResponseError(response, 'Error adding client');
            return
        } finally {
            this.setState({isSaving: false});
        }

        this.props.onHide();
    }

    cancelAddClient() {
        this.props.onHide();
    }

    render() {
        return <Modal
            title="Add Client"
            visible={this.props.visible}
            onOk={() => this.addClient()}
            onCancel={() => this.cancelAddClient()}
        >
            <Spin spinning={this.state.isSaving}>
                <Form layout="vertical">
                    <Form.Item label="Realm:">
                        <Select onChange={value => this.setState({selectedRealm: value})}>
                            {this.state.trackers.map(tracker => (
                                <Select.Option key={tracker.name} value={tracker.name}>
                                    {tracker.display_name}
                                </Select.Option>
                            ))}
                        </Select>
                    </Form.Item>
                    <Form.Item label="Instance Type:" defaultValue="managed_libtorrent">
                        <Select onChange={value => this.setState({selectedInstanceType: value})}>
                            <Select.Option value="managed_libtorrent">Managed Libtorrent</Select.Option>
                            <Select.Option value="managed_transmission">Managed Transmission</Select.Option>
                        </Select>
                    </Form.Item>
                </Form>
            </Spin>
        </Modal>;
    }
}
