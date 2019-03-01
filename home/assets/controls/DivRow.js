import PropTypes from 'prop-types';
import React from 'react';

const sizes = {
    small: 8,
    medium: 16,
    large: 24,
};

export class DivRow extends React.PureComponent {
    static propTypes = {
        size: PropTypes.any,
    };

    static defaultProps = {
        size: 'medium',
    };

    render() {
        let height;
        if (typeof this.props.size === 'number') {
            height = this.props.size;
        } else {
            height = sizes[this.props.size];
        }
        return <div style={{marginBottom: height}}>
            {this.props.children}
        </div>
    }
}
