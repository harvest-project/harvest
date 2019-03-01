import {Alert, Button, Col, Form, Input, message, Row, Tooltip} from 'antd';
import {APIHelper} from 'home/assets/api/APIHelper';
import {Timer} from 'home/assets/controls/Timer';
import {UIContext} from 'home/assets/contexts';
import {DivRow} from 'home/assets/controls/DivRow';
import React from 'react';
import {TorrentsAPI} from 'torrents/assets/TorrentsAPI';

const fieldLayout = {
    wrapperCol: {sm: 24},
};

const submitLayout = {
    wrapperCol: {sm: 24, md: 24},
};

export class AlcazarClientSettings extends React.Component {
    static contextType = UIContext;

    constructor(props) {
        super(props);

        this.state = {
            baseUrl: '',
            token: '',
            isSaving: false,

            isTesting: false,
            testResult: null,
            testMessage: null,
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
                data = await TorrentsAPI.getAlcazarClientConfig();
            } catch (response) {
                await APIHelper.showResponseError(response, 'Failed to load config');
                return;
            }
            this.setState({
                baseUrl: data.base_url,
                token: data.token,
            });
        });
    }

    // Fired by the timer to refresh the config data
    async refreshAlcazarConfig() {
        let data;
        try {
            data = await TorrentsAPI.getAlcazarClientConfig();
        } catch (response) {
            await APIHelper.showResponseError(response, 'Failed to refresh config');
            return;
        }
        this.setState({
            config: data,
        });
    }

    async saveAlcazarConfig() {
        this.setState({isSaving: true});
        try {
            await TorrentsAPI.saveAlcazarClientConfig(this.state.baseUrl, this.state.token);
        } catch (response) {
            await APIHelper.showResponseError(response, 'Failed to save settings');
            return;
        } finally {
            this.setState({isSaving: false});
        }

        message.success('Saved Redacted settings');
    }

    async testConnection() {
        this.setState({isTesting: true});
        try {
            const response = await TorrentsAPI.testAlcazarConnection();
            if (response.success) {
                this.setState({isTesting: false, testResult: true, testMessage: 'Successful connection to Alcazar'});
            } else {
                this.setState({isTesting: false, testResult: false, testMessage: response.detail});
            }
        } catch (exception) {
            this.setState({
                isTesting: false,
                testResult: false,
                testMessage: <ResponseErrorDisplay response={exception} additionalMessage="Connection failed"/>,
            });
        }
    }

    render() {
        return <Row gutter={24}>
            <Timer interval={1000} onInterval={() => this.refreshAlcazarConfig()}/>

            <Col sm={24} md={12} lg={10}>
                <Form layout="vertical" onSubmit={e => {
                    e.preventDefault();
                    this.saveAlcazarConfig()
                }}>
                    <h1>Alcazar Connection Settings</h1>

                    <Form.Item label="Base URL:" {...fieldLayout}>
                        <Input type='text' value={this.state.baseUrl}
                               onChange={event => this.setState({baseUrl: event.target.value})}/>
                    </Form.Item>

                    <Form.Item label="Token:" {...fieldLayout}>
                        <Input type="text" value={this.state.token}
                               onChange={event => this.setState({token: event.target.value})}/>
                    </Form.Item>

                    <Form.Item {...submitLayout}>
                        <Button type="primary" htmlType="submit" block loading={this.state.isSaving}>Save</Button>
                    </Form.Item>
                </Form>
            </Col>

            <Col sm={24} md={12} lg={10}>
                <h1>Status / Control</h1>

                <DivRow size="medium">
                    <Tooltip title="Make sure to save your new settings before testing.">
                        <Button type="primary" htmlType="button" block loading={this.state.isTesting}
                                onClick={() => this.testConnection()}>
                            Test Connection
                        </Button>
                    </Tooltip>
                </DivRow>

                {this.state.testResult === null ? null :
                    <DivRow>
                        <Alert type={this.state.testResult ? 'success' : 'error'} message={this.state.testMessage}/>
                    </DivRow>
                }
            </Col>
        </Row>;
    }
}
