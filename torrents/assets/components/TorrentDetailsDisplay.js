import {Alert, Button, Col, Popconfirm, Progress, Row, Statistic, Tooltip} from 'antd';
import {formatBytes, formatDateStringHuman} from 'home/assets/utils';
import PropTypes from 'prop-types';
import React from 'react';
import {getTorrentStatusDisplay, shortenInfoHash} from 'torrents/assets/utils';
import {TorrentsAPI} from 'torrents/assets/TorrentsAPI';

export class TorrentDetailsDisplay extends React.Component {
    static propTypes = {
        torrent: PropTypes.object.isRequired,
        onDelete: PropTypes.func.isRequired,
    };

    downloadZip() {
        window.location = TorrentsAPI.getDownloadTorrentZipUrl(this.props.torrent.id);
    }

    render() {
        const t = this.props.torrent;
        return <Row gutter={16}>
            <Col xs={24}>
                <p>
                    <b>Status:</b> {getTorrentStatusDisplay(t.status)}<br/>
                    <b>Info Hash:</b> <Tooltip title={t.info_hash}>{shortenInfoHash(t.info_hash)}</Tooltip><br/>
                    <b>Path:</b> {t.download_path}<br/>
                    <b>Client:</b> {t.client}<br/>
                </p>
            </Col>

            <Col xs={24} style={{paddingBottom: 12}}>
                <Progress percent={Math.floor(t.progress * 100)} size="large"/>
            </Col>

            <Col xs={8}>
                <Statistic title="Size" value={formatBytes(t.size)}/>
            </Col>
            <Col xs={8}>
                <Statistic title="Downloaded" value={formatBytes(t.downloaded)}/>
            </Col>
            <Col xs={8}>
                <Statistic title="Uploaded" value={formatBytes(t.uploaded)}/>
            </Col>
            <Col xs={8}>
                <Statistic title="Download Speed" value={formatBytes(t.download_rate) + '/s'}/>
            </Col>
            <Col xs={8}>
                <Statistic title="Upload Speed" value={formatBytes(t.upload_rate) + '/s'}/>
            </Col>
            <Col xs={8}>
                <Statistic title="Date Added" value={formatDateStringHuman(t.added_datetime)}/>
            </Col>

            {t.error ?
                <Col xs={24} style={{paddingTop: 8, paddingBottom: 8}}>
                    <Alert type="error" message="Torrent Error" description={t.error}/>
                </Col>
                : null
            }

            {t.tracker_error ?
                <Col xs={24} style={{paddingTop: 8, paddingBottom: 8}}>
                    <Alert type="error" message="Tracker Error" description={t.tracker_error}/>
                </Col>
                : null
            }

            <Col xs={24} style={{paddingTop: 8, paddingBottom: 8}}>
                <Button htmlType="button" type="primary" icon="download"
                        onClick={() => this.downloadZip()}>
                    Download
                </Button>
                {' '}
                <Popconfirm title="Are you sure?" onConfirm={() => this.props.onDelete()}>
                    <Button htmlType="button" type="danger" icon="delete">Delete</Button>
                </Popconfirm>
            </Col>
        </Row>;
    }
}
