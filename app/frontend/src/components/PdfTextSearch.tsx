import * as React from 'react';
import { Viewer } from '@react-pdf-viewer/core';
import { defaultLayoutPlugin } from '@react-pdf-viewer/default-layout';
import type { SingleKeyword } from '@react-pdf-viewer/search';

import '@react-pdf-viewer/core/lib/styles/index.css';
import '@react-pdf-viewer/default-layout/lib/styles/index.css';

interface JumpToFirstMatchExampleProps {
    fileUrl: string;
    keyword: SingleKeyword | SingleKeyword[];
}

const HighlightKeywords: React.FC<JumpToFirstMatchExampleProps> = ({
    fileUrl,
    keyword,
}) => {
    const [isDocumentLoaded, setDocumentLoaded] = React.useState(false);
    const handleDocumentLoad = () => setDocumentLoaded(true);

    const defaultLayoutPluginInstance = defaultLayoutPlugin();
    const { toolbarPluginInstance } = defaultLayoutPluginInstance;
    const { searchPluginInstance } = toolbarPluginInstance;
    const { highlight } = searchPluginInstance;

    React.useEffect(() => {
        if (isDocumentLoaded) {
            highlight(keyword);
        }
    }, [isDocumentLoaded]);

    return (
        <div
            style={{
                border: '1px solid rgba(0, 0, 0, 0.3)',
                height: '90vh',
            }}
        >
            <Viewer
                fileUrl={fileUrl}
                plugins={[defaultLayoutPluginInstance]}
                onDocumentLoad={handleDocumentLoad}
            />
        </div>
    );
};

export default HighlightKeywords;
