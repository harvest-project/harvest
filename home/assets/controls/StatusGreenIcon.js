import React from 'react';
import {CheckCircleOutlined, CloseCircleOutlined, WarningOutlined} from '@ant-design/icons';

export function StatusIcon(props) {
    if (props.status === 'green') {
        return <CheckCircleOutlined style={{color: '#52c41a'}}/>;
    } else if (props.status === 'yellow') {
        return <WarningOutlined style={{color: '#ddc000'}}/>;
    } else if (props.status === 'red') {
        return <CloseCircleOutlined style={{color: 'red'}}/>;
    }
}
