import {Icon, Layout} from 'antd';
import {APIHelper} from 'home/assets/api/APIHelper';
import {AuthAPI} from 'home/assets/api/AuthAPI';
import {HarvestContext} from 'home/assets/context';
import React from 'react';
import styles from './HarvestHeader.less';

const sizes = {
    small: 8,
    medium: 16,
    large: 24,
};

export class HarvestHeader extends React.Component {
    static contextType = HarvestContext;

    logout = async () => {
        try {
            await AuthAPI.logout();
        } catch (response) {
            await APIHelper.showResponseError(response);
        }
        this.context.user = null;
    };

    render() {
        return <Layout.Header className={styles['header-container']}>
            <div className={styles['header-button']} onClick={this.logout}>
                <Icon type="logout"/> Logout
            </div>
        </Layout.Header>
    }
}
