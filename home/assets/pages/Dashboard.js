import {Card, Col, Progress, Row} from 'antd';
import {HarvestContext} from 'home/assets/context';
import {DivRow} from 'home/assets/controls/DivRow';
import {observer} from 'mobx-react';
import React from 'react';

@observer
export class Dashboard extends React.Component {
    static contextType = HarvestContext;

    render() {
        return <div>
            <DivRow>
                <h2>Welcome to Harvest, {this.context.user.full_name}.</h2>
            </DivRow>
            <Row gutter={16}>
                {[0, 1, 2, 3, 4, 5].map(i => (
                    <Col key={i} xs={12} sm={8} lg={6} style={{marginBottom: 16}}>
                        <Card size="small" style={{textAlign: 'center'}} title="Space on /">
                            <Progress type="circle" percent={75} width={100}/>
                        </Card>
                    </Col>
                ))}
            </Row>
        </div>;
    }
}
