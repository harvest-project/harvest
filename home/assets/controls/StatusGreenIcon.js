import React from 'react';
import {Icon} from 'antd';

export function StatusIcon(props) {
    if (props.status === 'green') {
        return <Icon type="check-circle" style={{color: '#52c41a'}}/>;
    } else if (props.status === 'yellow') {
        return <Icon type="warning" style={{color: '#ddc000'}}/>;
    } else if (props.status === 'red') {
        return <Icon type="close-circle" style={{color: 'red'}}/>;
    }
}
