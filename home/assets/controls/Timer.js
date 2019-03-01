import PropTypes from 'prop-types';
import React from 'react';

export class Timer extends React.Component {
    static propTypes = {
        interval: PropTypes.number,
        onInterval: PropTypes.func,
        fireImmediately: PropTypes.bool,
    };

    constructor(props) {
        super(props);

        this.interval = null;
        this.running = false;
    }

    componentDidMount() {
        this.running = true;

        if (this.props.fireImmediately) {
            this.onInterval();
        } else {
            this.interval = setTimeout(this.onInterval.bind(this), this.props.interval);
        }
    }

    async onInterval() {
        const start = new Date(),
            result = this.props.onInterval();

        if (result) {
            await result;
        }

        if (this.running) {
            const timeTaken = new Date() - start,
                nextTimeout = Math.max(0, this.props.interval - timeTaken);
            this.interval = setTimeout(this.onInterval.bind(this), nextTimeout);
        }
    }

    componentWillUnmount() {
        this.running = false;

        if (this.interval !== null) {
            clearTimeout(this.interval);
            this.interval = null;
        }
    }

    render() {
        return null;
    }
}
