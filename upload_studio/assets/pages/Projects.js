import {Table} from 'antd';
import {APIHelper} from 'home/assets/api/APIHelper';
import {HarvestContext} from 'home/assets/context';
import {Timer} from 'home/assets/controls/Timer';
import React from 'react';
import {Link} from 'react-router-dom';
import {UploadStudioAPI} from 'upload_studio/assets/UploadStudioAPI';
import {UploadStudioUrls} from 'upload_studio/assets/UploadStudioUrls';
import {formatDateTimeStringISO} from 'home/assets/utils';
import {DivRow} from 'home/assets/controls/DivRow';

export class Projects extends React.Component {
    static contextType = HarvestContext;

    constructor(props) {
        super(props);

        this.columns = [
            {
                title: 'ID',
                dataIndex: 'id',
                width: 80,
            },
            {
                title: 'Created',
                dataIndex: 'created_datetime',
                render: data => formatDateTimeStringISO(data),
                width: 168,
            },
            {
                title: 'Status',
                dataIndex: 'status',
                width: 80,
            },
            {
                title: 'Name',
                dataIndex: 'name',
                render: (data, record) => <Link to={UploadStudioUrls.project.replace(':id', record.id)}>
                    {data}
                </Link>,
            },
        ];

        this.state = {
            loading: false,
            projectsActive: null,
            projectsHistory: null,
        };

        this.onRow = record => ({
            onClick: () => this.selectRow(record),
        });
    }

    componentDidMount() {
        this.refreshProjects(true);
    }

    async refreshProjects(modalLoading = false) {
        if (!modalLoading && this.state.loading) {
            return; // Do not supersede a modal (main) loading request
        }

        this.setState({
            loading: modalLoading,
        });

        let data;

        try {
            data = await UploadStudioAPI.getProjects();
        } catch (response) {
            await APIHelper.showResponseError(response, 'Failed to load projects');
            return;
        }

        this.setState({
            loading: false,
            projectsActive: data.active,
            projectsHistory: data.history,
        });

    }

    render() {
        return <div>
            <Timer interval={3000} onInterval={() => this.refreshProjects()}/>

            <h2>Active Projects</h2>

            <DivRow>
                <Table
                    size="small"
                    dataSource={this.state.projectsActive}
                    loading={this.state.loading}
                    columns={this.columns}
                    rowKey="id"
                    onRow={this.onRow}
                    pagination={false}
                />
            </DivRow>

            <h2>Finished Projects (Last 50)</h2>

            <Table
                size="small"
                dataSource={this.state.projectsHistory}
                loading={this.state.loading}
                columns={this.columns}
                rowKey="id"
                onRow={this.onRow}
                pagination={false}
            />
        </div>;
    }
}
