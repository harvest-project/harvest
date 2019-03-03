import {Form, Input, Tag} from 'antd';
import {DivRow} from 'home/assets/controls/DivRow';
import PropTypes from 'prop-types';
import React from 'react';

export class DownloadLocationPatternInput extends React.Component {
    static propTypes = {
        value: PropTypes.string.isRequired,
        onChange: PropTypes.func.isRequired,
    };

    constructor(props) {
        super(props);
    }

    addComponent(key) {
        this.props.onChange(this.props.value + key)
    }

    getComponents() {
        const components = [
            {
                key: '{torrent_file.info_hash}',
                description: '40 character lowercase info hash of the torrent',
                example: 'e1de9d536ddf849ead2497309e39a0ffedcfa001',
            },
            {
                key: '{torrent_file.name}',
                description: 'Original name from the .torrent file',
                example: 'Some directory name the uploader used',
            },
        ];
        if (this.props.tracker) {
            components.push(...[
                {
                    key: '{torrent_info.realm.name}',
                    description: 'Realm name of the torrent',
                    example: 'redacted',
                },
                {
                    key: '{torrent_info.tracker_id}',
                    description: 'ID of the torrent as retrieved from the tracker',
                    example: '97578',
                },
            ]);
            components.push(...this.props.tracker.download_location_components);
        }
        return components;
    }

    renderExample() {
        let value = this.props.value;
        for (const component of this.getComponents()) {
            value = value.replace(component.key, component.example);
        }
        return value;
    }

    renderPatternHelp() {
        return <span>
            It's recommended to include at least {'{torrent_file.info_hash}'} or {'{torrent_info.tracker_id}'}, but
            most importantly {'{torrent_file.name}'}.
            <br/>
            {this.props.value ? `Example result: ${this.renderExample()}` : <span>&nbsp;</span>}
        </span>;
    }

    render() {
        return <Form layout="vertical">
            <Form.Item label="Pattern:" help={this.renderPatternHelp()}>
                <Input value={this.props.value} onChange={e => this.props.onChange(e.target.value)}/>
            </Form.Item>
            <Form.Item label="Available pattern components:">
                {this.getComponents().map(comp => (
                    <DivRow key={comp.key} size="small">
                        <Tag onClick={() => this.addComponent(comp.key)}>{comp.key}</Tag>{' '}
                        <span className="light-text">e.g. {comp.example}</span>
                        <br/>
                        {comp.description}
                    </DivRow>
                ))}
            </Form.Item>
        </Form>;
    }
}
