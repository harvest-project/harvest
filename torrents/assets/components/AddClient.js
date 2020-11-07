import {Form, Input, message, Modal, Select, Spin} from 'antd';
import {APIHelper} from 'home/assets/api/APIHelper';
import {HarvestContext} from 'home/assets/context';
import {observer} from 'mobx-react';
import PropTypes from 'prop-types';
import React from 'react';
import {TorrentsAPI} from 'torrents/assets/TorrentsAPI';
import {PlusOutlined} from '@ant-design/icons';

const NEW_REALM = '__new';

@observer
export class AddClient extends React.Component {
    static propTypes = {
        visible: PropTypes.bool.isRequired,
        onHide: PropTypes.func.isRequired,
    };

    static contextType = HarvestContext;

    constructor(props) {
        super(props);

        this.state = {
            isAdding: false,
            selectedRealm: null,
            customRealmName: '',
            selectedInstanceType: null,
        };
    }

    get currentRealmName() {
        return this.state.selectedRealm !== NEW_REALM ?
            this.state.selectedRealm : this.state.customRealmName;
    }

    async addClient() {
        if (!this.currentRealmName || !this.state.selectedInstanceType) {
            message.error('Please select a realm and an instance type.');
            return;
        }

        this.setState({isAdding: true});
        try {
            await TorrentsAPI.addAlcazarClient(
                this.currentRealmName,
                this.state.selectedInstanceType,
            );
            this.context.realms = await TorrentsAPI.getRealms();
        } catch (response) {
            await APIHelper.showResponseError(response, 'Error adding client');
            return;
        } finally {
            this.setState({isAdding: false});
        }

        this.props.onHide();
    }

    render() {
        return <Modal
            title="Add Client"
            visible={this.props.visible}
            onOk={() => this.addClient()}
            onCancel={() => this.props.onHide()}
        >
            <Spin spinning={this.state.isAdding}>
                <Form layout="vertical">
                    <Form.Item label="Realm:">
                        <Select value={this.state.selectedRealm}
                                onChange={value => this.setState({selectedRealm: value})}>
                            {this.context.trackers
                                .filter(t => this.context.getRealmByName(t.name) === null)
                                .map(tracker => (
                                    <Select.Option key={tracker.name} value={tracker.name}>
                                        {tracker.name} ({tracker.display_name})
                                    </Select.Option>
                                ))}
                            {this.context.realms.map(realm => (
                                <Select.Option key={realm.name} value={realm.name}>
                                    {realm.name}
                                </Select.Option>
                            ))}

                            <Select.Option value={NEW_REALM}>
                                <PlusOutlined/> New Realm
                            </Select.Option>
                        </Select>
                    </Form.Item>

                    {this.state.selectedRealm === NEW_REALM ?
                        <Form.Item label="New Realm Name:">
                            <Input type="text" value={this.state.customRealmName}
                                   onChange={e => this.setState({customRealmName: e.target.value})}/>
                        </Form.Item>
                        : null}

                    <Form.Item label="Instance Type:">
                        <Select value={this.state.selectedInstanceType}
                                onChange={value => this.setState({selectedInstanceType: value})}>
                            <Select.Option value="managed_libtorrent">
                                Managed Libtorrent
                            </Select.Option>
                            <Select.Option value="managed_transmission">
                                Managed Transmission
                            </Select.Option>
                        </Select>
                    </Form.Item>
                </Form>
            </Spin>
        </Modal>;
    }
}
