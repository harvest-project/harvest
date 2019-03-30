import {Table} from 'antd';
import {APIHelper} from 'home/assets/api/APIHelper';
import {HarvestContext} from 'home/assets/context';
import {Timer} from 'home/assets/controls/Timer';
import React from 'react';
import {UploadStudioAPI} from 'upload_studio/assets/UploadStudioAPI';

export class Project extends React.Component {
    static contextType = HarvestContext;

    constructor(props) {
        super(props);

        this.columns = [
            {
                title: 'ID',
                dataIndex: 'id',
                sorter: true,
                width: 90,
            },
            {
                title: 'Status',
                dataIndex: 'status',
                width: 80,
            },
            {
                title: 'Type',
                dataIndex: 'executor_name',
                width: 100,
            },
            {
                title: 'Params',
                dataIndex: 'executor_kwargs',
            },
        ];

        this.state = {
            loading: false,
        };

        this.onRow = record => ({
            onClick: () => this.selectRow(record),
        });
    }

    componentDidMount() {
        this.refreshProject(true);
    }

    async refreshProject(modalLoading = false) {
        if (!modalLoading && this.state.loading) {
            return; // Do not supersede a modal (main) loading request
        }

        this.setState({
            loading: modalLoading,
        });

        let data;

        try {
            data = await UploadStudioAPI.getProject(this.props.match.params.id);
        } catch (response) {
            await APIHelper.showResponseError(response, 'Failed to load project');
            return;
        }

        this.setState({
            loading: false,
            project: data,
        });

    }

    render() {
        return <div>
            <Timer interval={3000} onInterval={() => this.refreshProject()}/>

            <h2>Project {this.state.project ? this.state.project.name : '-'}</h2>

            <Table
                size="small"
                dataSource={this.state.project ? this.state.project.steps : []}
                loading={this.state.loading}
                columns={this.columns}
                rowKey="id"
                onRow={this.onRow}
            />
        </div>;
    }
}
