import React from 'react';
import {Icon} from 'antd';

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
                <Icon type="robot" style={{fontSize: 48}}/><br/>
                <br/>
                <br/>
                <pre>{this.state.error.message}</pre>
                <pre>{this.state.error.stack}</pre>
            </h1>;
        }

        return this.props.children;
    }
}
