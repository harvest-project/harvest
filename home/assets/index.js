import 'antd/dist/antd.css';
import {Auth} from 'home/assets/components/Auth';
import {HarvestContext} from 'home/assets/context';
import 'home/assets/index.css';
import {HarvestStore} from 'home/assets/store';
import React from 'react';
import ReactDOM from 'react-dom';
import {BrowserRouter as Router} from 'react-router-dom';
import {LayoutBase} from './LayoutBase';

class Harvest extends React.Component {
    render() {
        return (
            <HarvestContext.Provider value={HarvestStore}>
                <Router>
                    <Auth>
                        <LayoutBase/>
                    </Auth>
                </Router>
            </HarvestContext.Provider>
        );
    }
}

ReactDOM.render(<Harvest/>, document.getElementById('react-root'));
