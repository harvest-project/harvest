import {Button} from 'antd';
import PropTypes from 'prop-types';
import React from 'react';
import {fileToBase64} from 'torrents/assets/utils';

export class UploadTorrent extends React.Component {
    static propTypes = {
        onChange: PropTypes.func.isRequired,
    };

    constructor(props) {
        super(props);

        this.fileRef = React.createRef();
    }

    selectFile() {
        this.fileRef.current.click();
    }

    async fileSelected(e) {
        const input = this.fileRef.current;
        if (input.files.length === 1) {
            const file = input.files[0],
                base64 = await fileToBase64(input.files[0]);
            this.props.onChange({
                name: file.name,
                size: file.size,
                base64: base64,
            })
        } else {
            this.props.onChange(null);
        }
    }

    render() {
        return <span>
            <Button htmlType="button" onClick={() => this.selectFile()}>Select File</Button>
            <input type="file" ref={this.fileRef} style={{display: 'none'}} onChange={e => this.fileSelected(e)}/>
        </span>;
    }
}
