import {Form, Input, message, Modal, Select, Spin} from 'antd';
import {APIHelper} from 'home/assets/api/APIHelper';
import {HarvestContext} from 'home/assets/context';
import {observer} from 'mobx-react';
import PropTypes from 'prop-types';
import React from 'react';
import {SelectDownloadLocation} from 'torrents/assets/controls/SelectDownloadLocation';
import {TorrentsAPI} from 'torrents/assets/TorrentsAPI';

@observer
export class AddTorrentFromTracker extends React.Component {
    static propTypes = {
        visible: PropTypes.bool.isRequired,
        onHide: PropTypes.func.isRequired,
    };

    static contextType = HarvestContext;

    constructor(props) {
        super(props);

        this.state = this.cleanState = {
            isAdding: false,
            selectedTracker: null,
            torrentId: null,
            downloadPath: '',
        }
    }

    async addTorrent() {
        if (!this.state.selectedTracker) {
            message.error('Please select a tracker.');
            return;
        }
        if (!this.state.torrentId) {
            message.error('Please select a file.');
            return;
        }
        if (!this.state.downloadPath) {
            message.error('Please enter a download path.');
            return;
        }

        this.setState({isAdding: true});
        try {
            await TorrentsAPI.addTorrentFromTracker(
                this.state.selectedTracker,
                this.state.torrentId,
                this.state.downloadPath,
            );
        } catch (response) {
            await APIHelper.showResponseError(response, 'Error adding client');
            return;
        } finally {
            this.setState({isAdding: false});
        }

        this.hide();
    }

    hide() {
        this.setState(this.cleanState);
        this.props.onHide();
    }

    render() {
        return <Modal
            title="Add Torrent From Tracker"
            visible={this.props.visible}
            onOk={() => this.addTorrent()}
            onCancel={() => this.hide()}
        >
            <Spin spinning={this.state.isAdding}>
                <Form layout="vertical">
                    <Form.Item label="Tracker:">
                        <Select value={this.state.selectedTracker}
                                onChange={value => this.setState({selectedTracker: value})}>
                            {this.context.trackers.map(tracker => (
                                <Select.Option key={tracker.name} value={tracker.name}>
                                    {tracker.display_name}
                                </Select.Option>
                            ))}
                        </Select>
                    </Form.Item>

                    <Form.Item label="Torrent ID:">
                        <Input type="text" value={this.state.torrentId}
                               onChange={e => this.setState({torrentId: e.target.value})}/>
                    </Form.Item>

                    <Form.Item label="Download Path:">
                        <SelectDownloadLocation
                            realmId={this.state.selectedTracker ? this.context.getRealmByName(
                                this.state.selectedTracker).id : null}
                            value={this.state.downloadPath}
                            onChange={value => this.setState({downloadPath: value})}
                        />
                    </Form.Item>
                </Form>
            </Spin>
        </Modal>;
    }
}
