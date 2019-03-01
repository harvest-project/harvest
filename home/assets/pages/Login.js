import {Button, Col, Form, Icon, Input, message, Row} from 'antd';
import {APIHelper} from 'home/assets/api/APIHelper';
import {AuthAPI} from 'home/assets/api/AuthAPI';
import {DataContext} from 'home/assets/contexts';
import React from 'react';

export class LoginForm extends React.Component {
    static contextType = DataContext;

    constructor(props) {
        super(props);
        this.state = {
            isLoading: false,
        };
    }

    handleSubmit = e => {
        e.preventDefault();
        this.props.form.validateFields((err, {username, password}) => {
            if (!err) {
                this.performLogin(username, password);
            }
        });
    };

    async performLogin(username, password) {
        try {
            this.context.user = await AuthAPI.login(username, password);
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
        const {getFieldDecorator} = this.props.form;
        return <Row style={{marginTop: 100}}>
            <Col xs={2} sm={6} md={7} lg={8} xl={9}/>
            <Col xs={20} sm={12} md={10} lg={8} xl={6}>
                <Form onSubmit={this.handleSubmit} className="login-form">
                    <h1>Harvest Login</h1>

                    <Form.Item>
                        {getFieldDecorator('username', {
                            rules: [{required: true, message: 'Please input your username!'}],
                        })(
                            <Input prefix={<Icon type="user" style={{color: 'rgba(0,0,0,.25)'}}/>}
                                   placeholder="Username"/>,
                        )}
                    </Form.Item>
                    <Form.Item>
                        {getFieldDecorator('password', {
                            rules: [{required: true, message: 'Please input your password!'}],
                        })(
                            <Input prefix={<Icon type="lock" style={{color: 'rgba(0,0,0,.25)'}}/>} type="password"
                                   placeholder="Password"/>,
                        )}
                    </Form.Item>
                    <Form.Item>
                        <Button type="primary" htmlType="submit" block loading={this.isLoading}>
                            Log in
                        </Button>
                    </Form.Item>
                </Form>
            </Col>
        </Row>;
    }
}

export const Login = Form.create({name: 'login'})(LoginForm);
