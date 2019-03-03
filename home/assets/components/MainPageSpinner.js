import {Spin} from 'antd';
import {HarvestContext} from 'home/assets/context';
import {observer} from 'mobx-react';
import React from 'react';

@observer
export class MainPageSpinner extends React.Component {
    static contextType = HarvestContext;

    render() {
        return <Spin spinning={this.context.numLoading > 0}>
            {this.props.children}
        </Spin>
    }
}
