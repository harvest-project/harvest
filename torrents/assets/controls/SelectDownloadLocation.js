import {Icon, Input, Select} from 'antd';
import {HarvestContext} from 'home/assets/context';
import {DivRow} from 'home/assets/controls/DivRow';
import {observer} from 'mobx-react';
import PropTypes from 'prop-types';
import React from 'react';

const __CUSTOM = '__custom';

@observer
export class SelectDownloadLocation extends React.Component {
    static contextType = HarvestContext;

    static propTypes = {
        onChange: PropTypes.func.isRequired,
        value: PropTypes.string.isRequired,
        realmId: PropTypes.number,
    };

    constructor(props) {
        super(props);

        this.state = {
            locations: null,
            isCustom: false,
        }
    }

    onChange(value) {
        if (value === __CUSTOM) {
            this.props.onChange('');
        } else {
            this.props.onChange(value);
        }
    }

    render() {
        if (this.props.realmId === null) {
            return <Select disabled value={null}>
                <Select.Option value={null}>No realm selected</Select.Option>
            </Select>;
        }

        const locations = this.context.getDownloadLocationsForRealm(this.props.realmId);
        const isCustom = this.props.value !== null && !locations.some(l => l.pattern === this.props.value);

        return <div>
            <DivRow>
                <Select value={isCustom ? __CUSTOM : this.props.value} onChange={value => this.onChange(value)}>
                    {locations.map(location => (
                        <Select.Option value={location.pattern}>{location.pattern}</Select.Option>
                    ))}
                    <Select.Option key="custom" value={__CUSTOM}>
                        <Icon type="plus"/> Custom Location
                    </Select.Option>
                </Select>
            </DivRow>

            {isCustom ? <DivRow>
                <Input value={this.props.value} onChange={e => this.onChange(e.target.value)}/>
            </DivRow> : null}
        </div>;
    }
}
