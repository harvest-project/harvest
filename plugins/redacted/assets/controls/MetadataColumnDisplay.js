import React from 'react';
import PropTypes from 'prop-types';

export class MetadataColumnDisplay extends React.Component {
    static propTypes = {
        torrentInfo: PropTypes.object,
    };

    render() {
        const group = this.props.torrentInfo.metadata.group,
            torrent = this.props.torrentInfo.metadata.torrent;
        return <span>
            {` ${group.joined_artists} - ${group.name}`}
            <span style={{fontStyle: 'italic', color: 'gray'}}>
                &nbsp;{` ${torrent.remaster_year}`}
                {torrent.remaster_year !== group.year ? ` (${group.year})` : ''}
                {` ${torrent.media} - ${torrent.format} - ${torrent.encoding}`}
            </span>
        </span>;
    }
}
