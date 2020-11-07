import React from 'react';
import {Icon} from 'antd';
import {RobotOutlined} from '@ant-design/icons';

export class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            hasError: false,
        };
    }

    static getDerivedStateFromError(error) {
        return {
            hasError: true,
            error: error,
        };
    }

    componentDidCatch(error, info) {
    }

    render() {
        if (this.state.hasError) {
            // You can render any custom fallback UI
            return <h1>
                <RobotOutlined style={{size: 40}}/>
                <br/>
                <br/>
                <pre>{this.state.error.message}</pre>
                <pre>{this.state.error.stack}</pre>
            </h1>;
        }

        return this.props.children;
    }
}
