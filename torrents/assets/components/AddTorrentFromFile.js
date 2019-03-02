import {Form, Input, message, Modal, Select, Spin} from 'antd';
import {APIHelper} from 'home/assets/api/APIHelper';
import {DataContext} from 'home/assets/contexts';
import {formatBytes} from 'home/utils';
import {observer} from 'mobx-react';
import PropTypes from 'prop-types';
import React from 'react';
import {UploadTorrent} from 'torrents/assets/components/UploadTorrent';
import {TorrentsAPI} from 'torrents/assets/TorrentsAPI';

@observer
export class AddTorrentFromFile extends React.Component {
    static propTypes = {
        visible: PropTypes.bool.isRequired,
        onHide: PropTypes.func.isRequired,
    };

    static contextType = DataContext;

    constructor(props) {
        super(props);

        this.state = this.cleanState = {
            isAdding: false,
            selectedRealm: null,
            selectedFile: null,
            downloadPath: '',
        }
    }

    async addTorrent() {
        if (!this.state.selectedRealm) {
            message.error('Please select a realm.');
            return;
        }
        if (!this.state.selectedFile) {
            message.error('Please select a file.');
            return;
        }
        if (!this.state.downloadPath) {
            message.error('Please enter a download path.');
            return;
        }

        this.setState({isAdding: true});
        try {
            await TorrentsAPI.addTorrentFromFile(
                this.state.selectedRealm,
                this.state.selectedFile.base64,
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
            title="Add Torrent From File"
            visible={this.props.visible}
            onOk={() => this.addTorrent()}
            onCancel={() => this.hide()}
        >
            <Spin spinning={this.state.isAdding}>
                <Form layout="vertical">
                    <Form.Item label="Realm:">
                        <Select value={this.state.selectedRealm}
                                onChange={value => this.setState({selectedRealm: value})}>
                            {this.context.realms.map(realm => (
                                <Select.Option key={realm.name} value={realm.name}>
                                    {realm.name}
                                </Select.Option>
                            ))}
                        </Select>
                    </Form.Item>

                    <Form.Item label="Torrent File:">
                        <UploadTorrent onChange={file => this.setState({selectedFile: file})}/>
                        {this.state.selectedFile ?
                            <span style={{display: 'inline-block', marginLeft: 8}}>
                                {this.state.selectedFile.name} ({formatBytes(this.state.selectedFile.size)})
                            </span>
                            : null}
                    </Form.Item>

                    <Form.Item label="Download Path:">
                        <Input type="text" value={this.state.downloadPath}
                               onChange={e => this.setState({downloadPath: e.target.value})}/>
                    </Form.Item>
                </Form>
            </Spin>
        </Modal>;
    }
}
