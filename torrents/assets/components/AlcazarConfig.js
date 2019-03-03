import {Button, Checkbox, Col, Form, Input, message, Row} from 'antd';
import {APIHelper} from 'home/assets/api/APIHelper';
import {Timer} from 'home/assets/controls/Timer';
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

            isSaving: false,
        }
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
            });
        });
    }

    // Fired by the timer to refresh the config data
    async refreshAlcazarConfig() {
        // let data;
        // try {
        //     data = await TorrentsAPI.getAlcazarClientConfig();
        // } catch (response) {
        //     await APIHelper.showResponseError(response, 'Failed to refresh config');
        //     return;
        // }
        // this.setState({
        //     config: data,
        // });
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
            });
        } catch (response) {
            await APIHelper.showResponseError(response, 'Failed to save settings');
            return;
        } finally {
            this.setState({isAdding: false});
        }

        message.success('Saved Alcazar settings');
    }

    async testConnection() {
        // this.setState({isTesting: true});
        // try {
        //     const response = await TorrentsAPI.testAlcazarConnection();
        //     if (response.success) {
        //         this.setState({isTesting: false, testResult: true, testMessage: 'Successful connection to Alcazar'});
        //     } else {
        //         this.setState({isTesting: false, testResult: false, testMessage: response.detail});
        //     }
        // } catch (exception) {
        //     this.setState({
        //         isTesting: false,
        //         testResult: false,
        //         testMessage: <ResponseErrorDisplay response={exception} additionalMessage="Connection failed"/>,
        //     });
        // }
    }

    render() {
        return <Row gutter={24}>
            <Timer interval={1000} onInterval={() => this.refreshAlcazarConfig()}/>

            <Col sm={24} md={12} lg={10}>
                <Form layout="vertical" onSubmit={e => {
                    e.preventDefault();
                    this.saveAlcazarConfig()
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
                        resources"
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
                        world (firewalled). Example: 9091-9191. You can add more ranges, use commas to separate them."
                    >
                        <Input type="text" value={this.state.localPortPoolsFmt}
                               onChange={event => this.setState({localPortPoolsFmt: event.target.value})}/>
                    </Form.Item>

                    <Form.Item
                        label="Peer Port Pools:"
                        {...fieldLayout}
                        help="Ports that clients can listen on for peers. Need to be opened in the firewall and port
                        forwarded, if behind NAT."
                    >
                        <Input type="text" value={this.state.peerPortPoolsFmt}
                               onChange={event => this.setState({peerPortPoolsFmt: event.target.value})}/>
                    </Form.Item>

                    <Form.Item {...submitLayout}>
                        <Button type="primary" htmlType="submit" block loading={this.state.isSaving}>Save</Button>
                    </Form.Item>
                </Form>
            </Col>
        </Row>;
    }
}
