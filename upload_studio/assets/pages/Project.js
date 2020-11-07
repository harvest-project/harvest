import {Alert, Button, Col, Dropdown, Menu, Popconfirm, Row, Table, Timeline, Tooltip} from 'antd';
import {APIHelper} from 'home/assets/api/APIHelper';
import {HarvestContext} from 'home/assets/context';
import {Timer} from 'home/assets/controls/Timer';
import React from 'react';
import {Redirect} from 'react-router-dom';
import {UploadStudioAPI} from 'upload_studio/assets/UploadStudioAPI';
import {TextBr} from 'home/assets/controls/TextBr';
import {DivRow} from 'home/assets/controls/DivRow';
import {UploadStudioUrls} from 'upload_studio/assets/UploadStudioUrls';
import {StepSettingsRegistry} from 'upload_studio/assets/StepSettingsRegistry.js';
import {
    CheckOutlined,
    DownOutlined,
    FileDoneOutlined,
    LockOutlined,
    PlayCircleOutlined,
} from '@ant-design/icons';

export class Project extends React.Component {
    static contextType = HarvestContext;

    constructor(props) {
        super(props);

        this.state = {
            project: null,
            isDeleted: false,
        };

        this.onRow = record => ({
            onClick: () => this.selectRow(record),
        });
    }

    get disableAll() {
        return !this.state.project || this.state.project.is_locked || this.state.project.is_finished;
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

    async projectDelete() {
        try {
            await UploadStudioAPI.deleteProject(this.state.project.id);
            this.setState({
                isDeleted: true,
            });
        } catch (response) {
            await APIHelper.showResponseError(response);
        }
    }

    async projectResetToStep(step) {
        try {
            await UploadStudioAPI.postProjectResetToStep(this.state.project.id, step);
        } catch (response) {
            await APIHelper.showResponseError(response);
        }
        await this.context.trackLoadingAsync(async () => this.refreshProject());
    }

    async projectFinish(step) {
        try {
            await UploadStudioAPI.postProjectFinish(this.state.project.id);
        } catch (response) {
            await APIHelper.showResponseError(response);
        }
        await this.context.trackLoadingAsync(async () => this.refreshProject());
    }

    async projectRunAll() {
        try {
            await UploadStudioAPI.postProjectRunAll(this.state.project.id);
        } catch (response) {
            await APIHelper.showResponseError(response);
        }
        await this.context.trackLoadingAsync(async () => this.refreshProject());
    }

    async projectRunOne() {
        try {
            await UploadStudioAPI.postProjectRunOne(this.state.project.id);
        } catch (response) {
            await APIHelper.showResponseError(response);
        }
        await this.context.trackLoadingAsync(async () => this.refreshProject());
    }

    async insertStep(index, executorName) {
        try {
            await UploadStudioAPI.postProjectInsertStep(this.state.project.id, index, executorName);
        } catch (response) {
            await APIHelper.showResponseError(response);
        }
        await this.context.trackLoadingAsync(async () => this.refreshProject());
    }

    getTimelineItemParams(step) {
        switch (step.status) {
            case 'pending':
                return {color: 'blue'};
            case 'running':
                return {
                    dot: <PlayCircleOutlined/>,
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
        const proj = this.state.project;
        const canReset = !proj.is_finished &&
            proj.steps.filter(s => s.index <= step.index).every(s => s.status === 'complete');
        const group = <Button.Group>
            {canReset ? (
                <Popconfirm title="Delete all files for steps after this and reset to here?"
                            onConfirm={() => this.projectResetToStep(step.index)}>
                    <Button type="danger" htmlType="button" disabled={this.disableAll}>Reset To
                        Here</Button>
                </Popconfirm>
            ) : null}
            {!this.disableAll ? (
                <Dropdown overlay={<Menu>
                    <Menu.Item
                        onClick={() => this.insertStep(step.index, 'fix_filename_track_numbers')}>
                        Fix filename track numbers
                    </Menu.Item>
                    <Menu.Item onClick={() => this.insertStep(step.index, 'strip_filename_spaces')}>
                        Strip filename spaces
                    </Menu.Item>
                    <Menu.Item onClick={() => this.insertStep(step.index, 'rename_files_to_tags')}>
                        Rename files to tags
                    </Menu.Item>
                    <Menu.Item
                        onClick={() => this.insertStep(step.index, 'verify_audio_files_integrity')}>
                        Verify audio files
                    </Menu.Item>
                    <Menu.Item
                        onClick={() => this.insertStep(step.index, 'upload_spectrals_to_imgur')}>
                        Upload spectrals to Imgur
                    </Menu.Item>
                </Menu>}>
                    <Button htmlType="button">Insert Step <DownOutlined/></Button>
                </Dropdown>
            ) : null}
        </Button.Group>;
        if (!React.Children.count(group.props.children)) {
            return null;
        }
        return group;
    }


    async ackWarning(e, warning) {
        e.preventDefault();
        try {
            await UploadStudioAPI.postProjectWarningAck(this.state.project.id, warning.id);
        } catch (response) {
            await APIHelper.showResponseError(response);
        }
        await this.context.trackLoadingAsync(async () => this.refreshProject());
    }

    renderStep(step) {
        const isCurrent = step.index === this.state.project.current_step;
        const SettingsComponent = StepSettingsRegistry.components[step.executor_name];
        return (
            <Timeline.Item key={step.id} {...this.getTimelineItemParams(step)}>
                <h4 style={{fontWeight: isCurrent ? 'bold' : 'normal'}}>
                    {step.id} {step.executor_name}
                    {SettingsComponent ? <>
                        &nbsp;
                        <SettingsComponent project={this.state.project} step={step}/>
                    </> : null}
                </h4>
                <DivRow>
                    <TextBr text={step.description}/>
                </DivRow>
                {step.warnings.map(warning => (
                    <DivRow key={warning.id}>
                        <Alert
                            type="warning"
                            message={<div>
                                <div style={{overflowX: 'auto'}}>
                                    <TextBr text={warning.message}/>
                                </div>
                                {warning.acked ? <CheckOutlined/> :
                                    <a onClick={e => this.ackWarning(e, warning)}>Ack</a>}
                            </div>}
                        />
                    </DivRow>
                ))}
                {step.errors.map(error => (
                    <DivRow key={error.id}>
                        <Alert
                            type="error"
                            message={<div style={{overflowX: 'auto'}}>
                                <TextBr text={error.message}/>
                            </div>}
                        />
                    </DivRow>
                ))}
                {this.renderStepActions(step)}
            </Timeline.Item>
        );
    }

    render() {
        if (this.state.isDeleted) {
            return <Redirect to={UploadStudioUrls.projects}/>;
        }

        const proj = this.state.project;
        if (!proj) {
            return null;
        }

        return <div>
            <Timer interval={3000} onInterval={() => this.refreshProject()}/>

            <h2>
                Project {proj.id}: {proj.name}
                {' '}
                {proj.is_locked ?
                    <Tooltip title="Project is locked because actions are being performed.">
                        <LockOutlined/>
                    </Tooltip> : null}
                {proj.is_finished ?
                    <Tooltip
                        title="Project is finished (all data has been deleted. No further actions are allowed.">
                        <FileDoneOutlined/>
                    </Tooltip> : null}
            </h2>

            <DivRow>
                <Button.Group>
                    <Button type="primary" htmlType="button" disabled={this.disableAll}
                            onClick={() => this.projectRunAll()}>
                        Run All
                    </Button>
                    <Button type="default" htmlType="button" disabled={this.disableAll}
                            onClick={() => this.projectRunOne()}>
                        Run One
                    </Button>
                    <Popconfirm title="Delete all files and reset from start?"
                                onConfirm={() => this.projectResetToStep(0)}>
                        <Button type="danger" htmlType="button"
                                disabled={this.disableAll}>Reset</Button>
                    </Popconfirm>
                    <Popconfirm title="Delete all files and mark project as finished?"
                                onConfirm={() => this.projectFinish()}>
                        <Button type="danger" htmlType="button"
                                disabled={this.disableAll}>Finish</Button>
                    </Popconfirm>
                    <Popconfirm title="Delete project including all files?"
                                onConfirm={() => this.projectDelete()}>
                        <Button type="danger" htmlType="button"
                                disabled={this.disableAll && !proj.is_finished}>
                            Delete
                        </Button>
                    </Popconfirm>
                </Button.Group>
            </DivRow>

            <Row gutter={24}>
                <Col xs={24} lg={8}>
                    <Timeline style={{marginTop: 16}}>
                        {proj.steps.map(step => this.renderStep(step))}
                    </Timeline>
                </Col>
                <Col xs={24} lg={16}>
                    <DivRow>
                        <Table
                            size="small"
                            columns={[
                                {title: 'Path', dataIndex: 'path'},
                            ]}
                            dataSource={proj.files}
                            rowKey="path"
                            pagination={false}
                        />
                    </DivRow>

                    <h3>Metadata:</h3>
                    <pre style={{maxHeight: 600, overflow: 'auto', whiteSpace: 'pre-wrap'}}>
                        {JSON.stringify(proj.metadata, null, 4)}
                    </pre>
                </Col>
            </Row>
        </div>;
    }
}
