import React from 'react';
import {Route} from 'react-router-dom';
import {MonitoringUrls} from 'monitoring/assets/MonitoringUrls';
import {Monitoring} from 'monitoring/assets/pages/Monitoring';

export class MonitoringRoutes extends React.Component {
    render() {
        return <div>
            <Route path={MonitoringUrls.monitoring} component={Monitoring}/>
        </div>;
    }
}
