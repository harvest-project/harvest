import {Breadcrumb, Layout} from 'antd';
import 'antd/dist/antd.css';
import {HarvestHeader} from 'home/assets/components/HarvestHeader';
import {MainPageSpinner} from 'home/assets/components/MainPageSpinner';
import {HomeRoutes} from 'home/assets/HomeRoutes';
import logo from 'home/assets/images/logo-68.png';
import {MainMenu} from 'home/assets/menu/MainMenu';
import {capitalizeWord} from 'home/assets/utils';
import React from 'react';
import {Route, Switch, withRouter} from 'react-router-dom';
import {SettingsRoutes} from 'settings/assets/SettingsRoutes';
import {TorrentsRoutes} from 'torrents/assets/TorrentsRoutes';
import styles from './LayoutBase.less';
import {MonitoringRoutes} from 'monitoring/assets/MonitoringRoutes';
import {ErrorBoundary} from 'home/assets/components/ErrorBoundary';
import {UploadStudioRoutes} from 'upload_studio/assets/UploadStudioRoutes';
import {RouteRegistry} from 'home/assets/PluginRegistry';

@withRouter
export class LayoutBase extends React.Component {
    state = {
        collapsed: false,
        isMobile: false,
    };

    onCollapse = (collapsed) => {
        this.setState({collapsed});
    };

    getDisplayPathItems() {
        const path = this.props.location.pathname.substring(1);
        if (path === '') {
            return ['Dashboard'];
        }
        const parts = path.split('/'),
            items = [];
        for (const part of parts) {
            const words = [];
            for (const word of part.split('-')) {
                words.push(capitalizeWord(word));
            }
            items.push(words.join(' '));
        }
        return items;
    }

    renderBreadcrumbItems() {
        const items = [
            <Breadcrumb.Item key="harvest">Harvest</Breadcrumb.Item>,
        ];
        for (const item of this.getDisplayPathItems()) {
            items.push(<Breadcrumb.Item key={item}>{item}</Breadcrumb.Item>);
        }
        return items;
    }

    render() {
        return (
            <Layout style={{minHeight: '100vh'}}>
                <Layout.Sider
                    collapsible
                    collapsed={this.state.collapsed}
                    onCollapse={this.onCollapse}
                    breakpoint="md"
                    collapsedWidth={this.state.isMobile ? 0 : undefined}
                    onBreakpoint={isMobile => this.setState({isMobile: isMobile})}
                >
                    <div className={styles.logo}><img src={logo}/></div>
                    <MainMenu/>
                </Layout.Sider>
                <Layout>
                    <Switch>
                        {RouteRegistry.fullPageRoutes}
                        <Route path="/" render={() => <>
                            <HarvestHeader/>

                            <Layout.Content style={{margin: '0 16px'}}>
                                <MainPageSpinner>
                                    <Breadcrumb style={{margin: '16px 0'}}>
                                        {this.renderBreadcrumbItems()}
                                    </Breadcrumb>
                                    <div style={{padding: 24, background: '#fff'}}>
                                        <ErrorBoundary>
                                            <HomeRoutes/>
                                            <MonitoringRoutes/>
                                            <SettingsRoutes/>
                                            <TorrentsRoutes/>
                                            <UploadStudioRoutes/>

                                            {RouteRegistry.pageRoutes}
                                        </ErrorBoundary>
                                    </div>
                                </MainPageSpinner>
                            </Layout.Content>

                            <Layout.Footer style={{textAlign: 'center'}}>
                                Harvest Project ©2019 Created by the Harvest team
                            </Layout.Footer>
                        </>}/>
                    </Switch>
                </Layout>
            </Layout>
        );
    }
}
