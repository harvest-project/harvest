import React from 'react';
import {Button, Modal} from 'antd';
import {UploadStudioAPI} from 'upload_studio/assets/UploadStudioAPI.js';
import {APIHelper} from 'home/assets/api/APIHelper.js';

export class SpectralSettings extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            isModalVisible: false,
            files: null,
        };
    }

    componentDidMount() {
        this.fetchFiles();
    }

    async fetchFiles() {
        const files = await UploadStudioAPI.getProjectStepFiles(
            this.props.project.id,
            this.props.step.id,
        );
        this.setState({
            files: files.spectrals,
        });
    }

    showSpectrals() {
        this.setState({isModalVisible: true});
        this.fetchFiles();
    }

    async confirmSpectrals() {
        try {
            await UploadStudioAPI.patchProjectStepExecutorKwargs(
                this.props.project.id,
                this.props.step.id,
                {
                    spectrals_confirmed: true,
                },
            );
            await UploadStudioAPI.postProjectRunAll(this.props.project.id);
        } catch (response) {
            await APIHelper.showResponseError(response, 'Failed to confirm spectrals.');
            return;
        }
        this.setState({isModalVisible: false});
    }

    render() {
        return <>
            <Modal
                title="Spectrals"
                visible={this.state.isModalVisible}
                onOk={() => this.confirmSpectrals()}
                onCancel={() => this.setState({isModalVisible: false})}
                style={{top: 20}}
                width="calc(100% - 40px)"
            >
                {(this.state.files || []).map(file => (
                    <div key={file}>
                        <img
                            src={UploadStudioAPI.getProjectStepFileUrl(
                                this.props.project.id, this.props.step.id, 'spectrals', file)}
                            style={{width: '100%'}}
                        />
                    </div>
                ))}
            </Modal>
            <Button
                htmlType="button" type="default" icon="setting" size="small"
                onClick={() => this.showSpectrals()}/>
        </>;
    }
}
