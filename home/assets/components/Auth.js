import {Spin} from 'antd';
import {APIHelper} from 'home/assets/api/APIHelper';
import {AuthAPI} from 'home/assets/api/AuthAPI';
import {DataContext} from 'home/assets/contexts';
import {Login} from 'home/assets/pages/Login';
import {clearContextType} from 'home/utils';
import {observer} from 'mobx-react';
import React from 'react';
import {withRouter} from 'react-router-dom';
import {TorrentsAPI} from 'torrents/assets/TorrentsAPI';
import {TrackersAPI} from 'trackers/assets/TrackersAPI';

@clearContextType
@withRouter
@observer
export class Auth extends React.Component {
    static contextType = DataContext;

    constructor(props) {
        super(props);
        this.state = {
            isLoading: true,
        }
    }

    componentDidMount() {
        this.loadAuth();
    }

    async loadAuth() {
        try {
            const user = await AuthAPI.getUser();
            await this.context.fetchInitial();
            this.context.user = user;
        } catch (response) {
            if (response.status !== 401) {
                await APIHelper.showResponseError(response, 'Failed to load auth status');
            }
        } finally {
            this.setState({isLoading: false});
        }
    }

    render() {
        return <Spin spinning={this.state.isLoading} style={{minHeight: '100vh'}}>
            {this.state.isLoading ? <div/> : (this.context.user ? this.props.children : <Login/>)}
        </Spin>
    }
}
