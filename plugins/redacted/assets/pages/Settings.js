import {Alert, Button, Col, Form, Input, message, Row, Tag, Tooltip} from 'antd';
import {APIHelper} from 'home/assets/api/APIHelper';
import {Timer} from 'home/assets/controls/Timer';
import {UIContext} from 'home/assets/contexts';
import {DivRow} from 'home/assets/controls/DivRow';
import {ResponseErrorDisplay} from 'home/assets/controls/ResponseErrorDisplay';
import {formatDateTimeString} from 'home/utils';
import {RedactedAPI} from 'plugins/redacted/assets/RedactedAPI';
import React from 'react';

const fieldLayout = {
    wrapperCol: {sm: 24},
};

const submitLayout = {
    wrapperCol: {sm: 24, md: 24},
};

export class Settings extends React.Component {
    static contextType = UIContext;

    constructor(props) {
        super(props);

        this.state = {
            username: '',
            password: '',
            isSaving: false,

            isTesting: false,
            testResult: null,
            testMessage: null,

            isClearingLoginData: false,
        }
    }

    componentDidMount() {
        this.loadConfig();
    }

    // Fired when the component is loaded, to populate initial data
    async loadConfig() {
        await this.context.trackLoadingAsync(async () => {
            let data;
            try {
                data = await RedactedAPI.getConfig();
            } catch (response) {
                await APIHelper.showResponseError(response, 'Failed to load config');
                return;
            }
            this.setState({
                username: data.username,
                password: data.password,
                config: data,
            });
        });
    }

    // Fired by the timer to refresh the config data
    async refreshConfig() {
        let data;
        try {
            data = await RedactedAPI.getConfig();
        } catch (response) {
            await APIHelper.showResponseError(response, 'Failed to refresh config');
            return;
        }
        this.setState({
            config: data,
        });
    }

    async saveConfig() {
        this.setState({isAdding: true});
        try {
            await RedactedAPI.saveConfig(this.state.username, this.state.password);
        } catch (response) {
            await APIHelper.showResponseError(response, 'Failed to save config');
            return;
        } finally {
            this.setState({isAdding: false});
        }

        message.success('Saved Redacted settings');
    }

    async clearLoginData() {
        this.setState({isClearingData: true});
        try {
            await RedactedAPI.clearLoginData();
        } catch (response) {
            await APIHelper.showResponseError(response, 'Failed to clear login data');
            return;
        } finally {
            this.setState({isClearingData: false});
        }

        message.success('Cleared Redacted login data');
    }

    async testConnection() {
        this.setState({isTesting: true});
        try {
            const response = await RedactedAPI.testConnection();
            if (response.success) {
                this.setState({isTesting: false, testResult: true, testMessage: 'Successful connection to Redacted'});
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

    renderLastLogin() {
        if (!this.state.config) {
            return null;
        }

        if (this.state.config.last_login_failed) {
            return <Tag color="red">Failed</Tag>;
        }

        if (this.state.config.last_login_datetime) {
            return <Tag color="green">Successful</Tag>;
        }

        return null;
    }

    render() {
        return <Row gutter={24}>
            <Timer interval={1000} onInterval={() => this.refreshConfig()}/>

            <Col sm={24} md={12} lg={10}>
                <Form layout="vertical" onSubmit={e => {
                    e.preventDefault();
                    this.saveConfig()
                }}>
                    <h1>Redacted.ch Settings</h1>

                    <Form.Item label="Username:" {...fieldLayout}>
                        <Input type="text" value={this.state.username}
                               onChange={event => this.setState({username: event.target.value})}/>
                    </Form.Item>

                    <Form.Item label="Password:" {...fieldLayout}>
                        <Input type="text" value={this.state.password}
                               onChange={event => this.setState({password: event.target.value})}/>
                    </Form.Item>

                    <Form.Item {...submitLayout}>
                        <Button type="primary" htmlType="submit" block loading={this.state.isAdding}>Save</Button>
                    </Form.Item>
                </Form>
            </Col>

            <Col sm={24} md={12} lg={10}>
                <h1>Status / Control</h1>

                <DivRow size="medium">
                    Last Login Date:&nbsp;
                    {this.state.config && this.state.config.login_datetime ?
                        formatDateTimeString(this.state.config.login_datetime) : '-'}<br/>

                    Last Login: {this.renderLastLogin()}
                </DivRow>

                <DivRow size="medium">
                    <Tooltip title="Make sure to save your new settings before testing.">
                        <Button type="primary" htmlType="button" block loading={this.state.isTesting}
                                onClick={() => this.testConnection()}>
                            Test Connection
                        </Button>
                    </Tooltip>
                </DivRow>

                {this.state.testResult === null ? null :
                    <DivRow size="medium">
                        <Alert type={this.state.testResult ? 'success' : 'error'} message={this.state.testMessage}/>
                    </DivRow>
                }

                <DivRow size="medium">
                    <Tooltip title="Clears the saves cookies, authkey, passkey, etc.">
                        <Button type="danger" htmlType="button" block loading={this.state.isClearingLoginData}
                                onClick={() => this.clearLoginData()}>
                            Clear Login Data
                        </Button>
                    </Tooltip>
                </DivRow>
            </Col>
        </Row>;
    }
}
