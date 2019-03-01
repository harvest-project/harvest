import {plugins} from 'home/assets/PluginRegistry';
import React from 'react';

export class PluginRoutes extends React.Component {
    constructor(props) {
        super(props);

        this.pluginsWithRoutes = [];
        for (const plugin of plugins) {
            if (plugin.routes) {
                this.pluginsWithRoutes.push(plugin);
            }
        }
    }

    render() {
        return <div>
            {this.pluginsWithRoutes.map(plugin => <plugin.routes key={plugin.pluginName}/>)}
        </div>
    }
}
