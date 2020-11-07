import {Button, Col, Form, Input, message, Row} from 'antd';
import {APIHelper} from 'home/assets/api/APIHelper';
import {AuthAPI} from 'home/assets/api/AuthAPI';
import {HarvestContext} from 'home/assets/context';
import React from 'react';
import {LockOutlined, UserOutlined} from '@ant-design/icons';

export class Login extends React.Component {
    static contextType = HarvestContext;

    constructor(props) {
        super(props);
        this.state = {
            isLoading: false,
            username: '',
            password: '',
        };
    }

    async performLogin(e) {
        try {
            const user = await AuthAPI.login(this.state.username, this.state.password);
            await this.context.fetchInitial();
            this.context.user = user;
            message.success(`Welcome, ${this.context.user.full_name || this.context.user.username}.`);
        } catch (response) {
            if (response.status === 400) {
                const data = await response.json();
                message.error(data.detail);
            } else {
                await APIHelper.showResponseError(response);
            }
        }
    }

    render() {
        return <Row style={{marginTop: 100}}>
            <Col xs={2} sm={6} md={7} lg={8} xl={9}/>
            <Col xs={20} sm={12} md={10} lg={8} xl={6}>
                <Form onFinish={() => this.performLogin()} className="login-form">
                    <h1>Harvest Login</h1>

                    <Form.Item>
                        <Input
                            prefix={<UserOutlined style={{color: 'rgba(0,0,0,.25)'}}/>}
                            placeholder="Username"
                            value={this.state.username}
                            onChange={e => this.setState({username: e.target.value})}
                            onSubmit={() => {
                                debugger;
                            }}
                        />
                    </Form.Item>
                    <Form.Item>
                        <Input
                            prefix={<LockOutlined style={{color: 'rgba(0,0,0,.25)'}}/>}
                            type="password"
                            placeholder="Password"
                            value={this.state.password}
                            onChange={e => this.setState({password: e.target.value})}
                        />
                    </Form.Item>
                    <Form.Item>
                        <Button
                            type="primary"
                            htmlType="submit"
                            block
                            loading={this.isLoading}
                        >
                            Log in
                        </Button>
                    </Form.Item>
                </Form>
            </Col>
        </Row>;
    }
}
