import {BibliotikUrls} from 'plugins/bibliotik/assets/BibliotikUrls';
import {Settings} from 'plugins/bibliotik/assets/pages/Settings';
import React from 'react';
import {Route} from 'react-router-dom';

export class Routes extends React.Component {
    render() {
        return <>
            <Route path={BibliotikUrls.settings} component={Settings}/>
        </>;
    }
}
