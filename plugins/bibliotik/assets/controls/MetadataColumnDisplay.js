import React from 'react';
import PropTypes from 'prop-types';

export class MetadataColumnDisplay extends React.Component {
    static propTypes = {
        torrentInfo: PropTypes.object,
    };

    render() {
        const torrent = this.props.torrentInfo.metadata.torrent;
        return <span>
            {torrent.joined_authors ? ` ${torrent.joined_authors} -` : ''}
            {` ${torrent.title}`}
            <span style={{fontStyle: 'italic', color: 'gray'}}>
                &nbsp;{` ${torrent.category}`}
                {torrent.language ? ', ' + torrent.language : ''}
                {torrent.format ? ', ' + torrent.format : ''}
                {torrent.year ? ', ' + torrent.year : ''}
            </span>
        </span>;
    }
}
