import PropTypes from 'prop-types';
import React from 'react';

export class ResponseErrorDisplay extends React.PureComponent {
    static propTypes = {
        additionalMessage: PropTypes.string,
        response: PropTypes.instanceOf(Response),
        responseJson: PropTypes.any,
    };

    render() {
        if (this.props.response.message) {
            return <span>{this.props.additionalMessage}: {this.props.response.message}</span>;
        }

        if (!this.props.response.ok) {
            return <span>
                {this.props.additionalMessage}:<br/>
                Server returned <b>{this.props.response.status} {this.props.response.statusText}</b><br/>

                {this.props.responseJson && this.props.responseJson.detail ?
                    <b>{this.props.responseJson.detail}</b> : null}
            </span>;
        }

        console.error('API call returned response:', response);
        return <span>A truly mysterious error! Details in console.</span>;
    }
}
