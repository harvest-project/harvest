import 'antd/dist/antd.css';
import {DataContext, UIContext} from 'home/assets/contexts';
import {Auth} from 'home/assets/components/Auth';
import 'home/assets/index.css';
import {DataStore, UIStore} from 'home/assets/stores';
import React from 'react';
import ReactDOM from 'react-dom';
import {BrowserRouter as Router} from 'react-router-dom';
import {LayoutBase} from './LayoutBase';

class Harvest extends React.Component {
    render() {
        return (
            <DataContext.Provider value={DataStore}>
                <UIContext.Provider value={UIStore}>
                    <Router>
                        <Auth>
                            <LayoutBase/>
                        </Auth>
                    </Router>
                </UIContext.Provider>
            </DataContext.Provider>
        );
    }
}

ReactDOM.render(<Harvest/>, document.getElementById('react-root'));
