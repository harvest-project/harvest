import {Button, Col, Form, Input, message, Row} from 'antd';
import {APIHelper} from 'home/assets/api/APIHelper';
import {HarvestContext} from 'home/assets/context';
import React from 'react';
import {CopyToClipboard} from 'react-copy-to-clipboard';
import {SettingsAPI} from 'settings/assets/SettingsAPI';
import {CopyOutlined} from '@ant-design/icons';

const fieldLayout = {
    wrapperCol: {sm: 24},
};

const submitLayout = {
    wrapperCol: {sm: 24, md: 24},
};

export class APISettings extends React.Component {
    static contextType = HarvestContext;

    constructor(props) {
        super(props);

        this.state = {
            token: '',
            isSaving: false,
        };
    }

    componentDidMount() {
        this.loadToken();
    }

    // Fired when the component is loaded, to populate initial data
    async loadToken() {
        await this.context.trackLoadingAsync(async () => {
            let data;
            try {
                data = await SettingsAPI.getToken();
            } catch (response) {
                await APIHelper.showResponseError(response, 'Failed to load token');
                return;
            }
            this.setState({
                token: data.token || '',
            });
        });
    }

    async generateToken() {
        let data;
        this.setState({isAdding: true});
        try {
            data = await SettingsAPI.generateToken(this.state.baseUrl, this.state.token);
        } catch (response) {
            await APIHelper.showResponseError(response, 'Failed to generate token');
            return;
        } finally {
            this.setState({isAdding: false});
        }

        this.setState({
            token: data.token,
        });

        message.success('Generated API token.');
    }

    render() {
        return <Row gutter={24}>
            <Col sm={24} md={12} lg={10}>
                <Form layout="vertical" onSubmit={e => {
                    e.preventDefault();
                    this.generateToken();
                }}>
                    <h1>Harvest API Settings</h1>

                    <Form.Item label="Token:" {...fieldLayout}>
                        <Input
                            type="text" value={this.state.token}
                            onChange={event => this.setState({token: event.target.value})}
                            addonAfter={
                                <CopyToClipboard
                                    text={this.state.token}
                                    onCopy={() => message.success('Copied!')}>
                                    <CopyOutlined/>
                                </CopyToClipboard>
                            }
                        />
                    </Form.Item>

                    <Form.Item {...submitLayout}>
                        <Button type="primary" htmlType="submit" block
                                loading={this.state.isSaving}>
                            Generate Token
                        </Button>
                    </Form.Item>
                </Form>
            </Col>
        </Row>;
    }
}
