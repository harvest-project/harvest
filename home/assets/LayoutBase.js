import {Breadcrumb, Layout} from 'antd';
import 'antd/dist/antd.css';
import {MainPageSpinner} from 'home/assets/components/MainPageSpinner';
import {HarvestHeader} from 'home/assets/components/HarvestHeader';
import {HomeRoutes} from 'home/assets/HomeRoutes';
import logo from 'home/assets/images/logo.png';
import {MainMenu} from 'home/assets/menu/MainMenu';
import {PluginRoutes} from 'home/assets/PluginRoutes';
import React from 'react';
import {SettingsRoutes} from 'settings/assets/SettingsRoutes';
import {TorrentsRoutes} from 'torrents/assets/TorrentsRoutes';
import styles from './LayoutBase.less';

const {Header, Sider, Content, Footer} = Layout;

export class LayoutBase extends React.Component {
    state = {
        collapsed: false,
        isMobile: false,
    };

    onCollapse = (collapsed) => {
        this.setState({collapsed});
    };

    render() {
        return (
            <Layout style={{minHeight: '100vh'}}>
                <Sider
                    collapsible
                    collapsed={this.state.collapsed}
                    onCollapse={this.onCollapse}
                    breakpoint="md"
                    collapsedWidth={this.state.isMobile ? 0 : undefined}
                    onBreakpoint={isMobile => this.setState({isMobile: isMobile})}
                >
                    <div className={styles.logo}><img src={logo}/></div>
                    <MainMenu/>
                </Sider>
                <Layout>
                    <HarvestHeader/>

                    <Content style={{margin: '0 16px'}}>
                        <MainPageSpinner>
                            <Breadcrumb style={{margin: '16px 0'}}>
                                <Breadcrumb.Item>User</Breadcrumb.Item>
                                <Breadcrumb.Item>Bill</Breadcrumb.Item>
                            </Breadcrumb>
                            <div style={{padding: 24, background: '#fff'}}>
                                <HomeRoutes/>
                                <SettingsRoutes/>
                                <TorrentsRoutes/>
                                <PluginRoutes/>
                            </div>
                        </MainPageSpinner>
                    </Content>

                    <Footer style={{textAlign: 'center'}}>
                        Harvest Project ©2019 Created by the Harvest team
                    </Footer>
                </Layout>
            </Layout>
        );
    }
}
