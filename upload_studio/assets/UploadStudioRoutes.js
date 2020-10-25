import React from 'react';
import {Route} from 'react-router-dom';
import {UploadStudioUrls} from 'upload_studio/assets/UploadStudioUrls';
import {Projects} from 'upload_studio/assets/pages/Projects';
import {Project} from 'upload_studio/assets/pages/Project';
import {StepSettingsRegistry} from 'upload_studio/assets/StepSettingsRegistry.js';
import {SpectralSettings} from 'upload_studio/assets/SpectralViewer.js';

export class UploadStudioRoutes extends React.Component {
    render() {
        return <div>
            <Route path={UploadStudioUrls.projects} exact component={Projects}/>
            <Route path={UploadStudioUrls.project} component={Project}/>
        </div>;
    }
}

StepSettingsRegistry.register('confirm_spectrals', SpectralSettings);
