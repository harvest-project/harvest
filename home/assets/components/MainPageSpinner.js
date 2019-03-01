import {Spin} from 'antd';
import {UIContext} from 'home/assets/contexts';
import {observer} from 'mobx-react';
import React from 'react';

@observer
export class MainPageSpinner extends React.Component {
    static contextType = UIContext;

    render() {
        return <Spin spinning={this.context.numLoading > 0}>
            {this.props.children}
        </Spin>
    }
}
