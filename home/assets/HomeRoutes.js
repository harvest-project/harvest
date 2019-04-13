import {HomeUrls} from 'home/assets/HomeUrls';
import {Dashboard} from 'home/assets/pages/Dashboard';
import React from 'react';
import {Route} from 'react-router-dom';

export const HomeRoutes = () => <>
    <Route exact path={HomeUrls.dashboard} component={Dashboard}/>
</>;
