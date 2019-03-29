import {Button, Checkbox, Col, Form, Input, message, Row} from 'antd';
import {APIHelper} from 'home/assets/api/APIHelper';
import {HarvestContext} from 'home/assets/context';
import React from 'react';
import {TorrentsAPI} from 'torrents/assets/TorrentsAPI';

const {TextArea} = Input;

const fieldLayout = {
    wrapperCol: {sm: 24},
};

const submitLayout = {
    wrapperCol: {sm: 24, md: 24},
};

export class AlcazarConfig extends React.Component {
    static contextType = HarvestContext;

    constructor(props) {
        super(props);

        this.state = {
            apiPort: '',
            transmissionSettingsJson: '',
            isDhtEnabled: false,
            localPortPoolsFmt: '',
            peerPortPoolsFmt: '',
            cleanDirectoriesOnRemove: false,
            cleanTorrentFileOnRemove: false,
            enableFilePreallocation: false,

            isSaving: false,
        };
    }

    componentDidMount() {
        this.loadAlcazarConfig();
    }

    // Fired when the component is loaded, to populate initial data
    async loadAlcazarConfig() {
        await this.context.trackLoadingAsync(async () => {
            let data;
            try {
                data = await TorrentsAPI.getAlcazarConfig();
            } catch (response) {
                await APIHelper.showResponseError(response, 'Failed to load config');
                return;
            }
            this.setState({
                apiPort: data.api_port,
                transmissionSettingsJson: data.transmission_settings_json,
                isDhtEnabled: data.is_dht_enabled,
                localPortPoolsFmt: data.local_port_pools_fmt,
                peerPortPoolsFmt: data.peer_port_pools_fmt,
                cleanDirectoriesOnRemove: data.clean_directories_on_remove,
                cleanTorrentFileOnRemove: data.clean_torrent_file_on_remove,
                enableFilePreallocation: data.enable_file_preallocation,
            });
        });
    }

    async saveAlcazarConfig() {
        this.setState({isAdding: true});
        try {
            await TorrentsAPI.saveAlcazarConfig({
                api_port: this.state.apiPort,
                transmission_settings_json: this.state.transmissionSettingsJson,
                is_dht_enabled: this.state.isDhtEnabled,
                local_port_pools_fmt: this.state.localPortPoolsFmt,
                peer_port_pools_fmt: this.state.peerPortPoolsFmt,
                clean_directories_on_remove: this.state.cleanDirectoriesOnRemove,
                clean_torrent_file_on_remove: this.state.cleanTorrentFileOnRemove,
                enable_file_preallocation: this.state.enableFilePreallocation,
            });
        } catch (response) {
            await APIHelper.showResponseError(response, 'Failed to save settings');
            return;
        } finally {
            this.setState({isAdding: false});
        }

        message.success('Saved Alcazar settings');
    }

    render() {
        return <Row gutter={24}>
            <Col sm={24} md={12} lg={10}>
                <Form layout="vertical" onSubmit={e => {
                    e.preventDefault();
                    this.saveAlcazarConfig();
                }}>
                    <Form.Item
                        label="API Port:"
                        {...fieldLayout}
                        help="The port that Alcazar uses to expose its API. If you change this, make sure to also update
                        the Harvest Alcazar Client settings to reflect the change. Applied on restart."
                    >
                        <Input type="text" value={this.state.apiPort}
                               onChange={event => this.setState({apiPort: event.target.value})}/>
                    </Form.Item>

                    <Form.Item
                        label="Transmission Settings JSON:"
                        {...fieldLayout}
                        help="Default settings to launch Transmission with. Applied on restart."
                    >
                        <TextArea value={this.state.transmissionSettingsJson}
                                  onChange={event => this.setState({transmissionSettingsJson: event.target.value})}
                                  autosize={{minRows: 4, maxRows: 10}}/>
                    </Form.Item>

                    <Form.Item
                        {...fieldLayout}
                        help="Enable or disable DHT. For private torrents, DHT is not used and disabling it can save
                        resources. Requires restart."
                    >
                        <Checkbox checked={this.state.isDhtEnabled}
                                  onChange={event => this.setState({isDhtEnabled: event.target.checked})}>
                            DHT Enabled
                        </Checkbox>
                    </Form.Item>

                    <Form.Item
                        label="Local Port Pools:"
                        {...fieldLayout}
                        help="Ports that are used for local communication with clients. Preferably not opened to the
                        world (firewalled). Example: 9091-9191. You can add more ranges, use commas to separate them.
                        Requires restart."
                    >
                        <Input type="text" value={this.state.localPortPoolsFmt}
                               onChange={event => this.setState({localPortPoolsFmt: event.target.value})}/>
                    </Form.Item>

                    <Form.Item
                        label="Peer Port Pools:"
                        {...fieldLayout}
                        help="Ports that clients can listen on for peers. Need to be opened in the firewall and port
                        forwarded, if behind NAT. Requires restart."
                    >
                        <Input type="text" value={this.state.peerPortPoolsFmt}
                               onChange={event => this.setState({peerPortPoolsFmt: event.target.value})}/>
                    </Form.Item>

                    <Form.Item
                        {...fieldLayout}
                        help="When removing a torrent, delete all directories that are empty (or would be empty after
                        cleaned with the &quot;Clean torrent file on remove&quot; option) going up the filesystem tree
                        until a non-empty directories is encountered"
                    >
                        <Checkbox checked={this.state.cleanDirectoriesOnRemove}
                                  onChange={event => this.setState({
                                      cleanDirectoriesOnRemove: event.target.checked,
                                  })}>
                            Clean Directories On Remove
                        </Checkbox>
                    </Form.Item>

                    <Form.Item
                        {...fieldLayout}
                        help="When cleaning the directories for a remove torrent, also remove a single .torrent file
                        in the directory if present, also a ReleaseInfo2.txt, if present. Do not touch the directory
                        if there are other files present."
                    >
                        <Checkbox checked={this.state.cleanTorrentFileOnRemove}
                                  onChange={event => this.setState({
                                      cleanTorrentFileOnRemove: event.target.checked,
                                  })}>
                            Clean Torrent File On Remove
                        </Checkbox>
                    </Form.Item>

                    <Form.Item
                        {...fieldLayout}
                        help="Fully preallocate all files when starting a torrent. Reduces fragmentation, but requires
                        all files to be written to disk when a torrent is added. If disabled, sparse files are used.
                        Requires restart."
                    >
                        <Checkbox checked={this.state.enableFilePreallocation}
                                  onChange={event => this.setState({
                                      enableFilePreallocation: event.target.checked,
                                  })}>
                            Enable File Preallocation
                        </Checkbox>
                    </Form.Item>

                    <Form.Item {...submitLayout}>
                        <Button type="primary" htmlType="submit" block loading={this.state.isSaving}>Save</Button>
                    </Form.Item>
                </Form>
            </Col>
        </Row>;
    }
}
