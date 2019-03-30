import {Alert, Col, Icon, Row, Table, Timeline} from 'antd';
import {APIHelper} from 'home/assets/api/APIHelper';
import {HarvestContext} from 'home/assets/context';
import {Timer} from 'home/assets/controls/Timer';
import React from 'react';
import {UploadStudioAPI} from 'upload_studio/assets/UploadStudioAPI';
import {TextBr} from 'home/assets/controls/TextBr';
import {DivRow} from 'home/assets/controls/DivRow';

export class Project extends React.Component {
    static contextType = HarvestContext;

    constructor(props) {
        super(props);

        this.state = {
            project: null,
        };

        this.onRow = record => ({
            onClick: () => this.selectRow(record),
        });
    }

    componentDidMount() {
        this.context.trackLoadingAsync(async () => this.refreshProject());
    }

    async refreshProject(modalLoading = false) {
        let data;

        try {
            data = await UploadStudioAPI.getProject(this.props.match.params.id);
        } catch (response) {
            await APIHelper.showResponseError(response, 'Failed to load project');
            return;
        }

        this.setState({
            project: data,
        });
    }

    getTimelineItemParams(step) {
        switch (step.status) {
            case 'pending':
                return {color: 'blue'};
            case 'running':
                return {
                    dot: <Icon type="play-circle"/>,
                    style: {fontSize: '16px'},
                };
            case 'warnings':
            case 'errors':
                return {color: 'red'};
            case 'complete':
            case 'finished':
                return {color: 'green'};
        }
        return {};
    }

    renderStepActions(step) {
        if (step.status === '') {

        }
    }

    render() {
        const proj = this.state.project;
        if (!proj) {
            return null;
        }
        return <div>
            <Timer interval={3000} onInterval={() => this.refreshProject()}/>

            <h2>Project {proj.name}</h2>

            <Row gutter={24}>
                <Col xs={24} lg={8}>
                    <Timeline style={{marginTop: 16}}>
                        {proj.steps.map(step => (
                            <Timeline.Item key={step.id} {...this.getTimelineItemParams(step)}>
                                <h4 style={{fontWeight: step.index === proj.current_step ? 'bold' : 'normal'}}>
                                    {step.executor_name}
                                </h4>
                                <p>{step.description}</p>
                                {step.warnings.map(warning => (
                                    <Alert type="warning" message={<span>warning.message</span>}/>
                                ))}
                                {step.errors.map(error => (
                                    <Alert type="error" message={<TextBr text={error.message}/>}/>
                                ))}
                                {this.renderStepActions(step)}
                            </Timeline.Item>
                        ))}
                    </Timeline>
                </Col>
                <Col xs={24} lg={16}>
                    <Table
                        size="small"
                        columns={[
                            {title: 'Path', dataIndex: 'path'},
                        ]}
                        dataSource={proj.files}
                        pagination={false}
                    />
                </Col>
            </Row>
            <
            /div>;;
            }
            };
