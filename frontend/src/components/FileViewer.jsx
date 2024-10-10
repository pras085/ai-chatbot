export const FileViewer = ({ file, onPreviewFile }) => {
    if (!file || !file.file_url) return null;

    const fileUrl = `http://localhost:8000${file.file_url}`;

    const handlePreview = () => {
        if (onPreviewFile) {
            onPreviewFile(file);
        }
    };

    const fileExtension = file.file_name.split('.').pop().toLowerCase();

    switch (fileExtension) {
        case 'pdf':
            return (
                <div onClick={handlePreview} style={{ cursor: 'pointer' }}>
                    <img src="/pdf-icon.png" alt="PDF" style={{ width: '50px', height: '50px' }} />
                    <span>{file.file_name}</span>
                </div>
            );
        case 'jpg':
        case 'jpeg':
        case 'png':
        case 'gif':
            return <img src={fileUrl} alt={file.file_name} style={{ maxWidth: '100%', cursor: 'pointer' }} onClick={handlePreview} />;
        default:
            return (
                <div onClick={handlePreview} style={{ cursor: 'pointer' }}>
                    <img src="/file-icon.png" alt="File" style={{ width: '50px', height: '50px' }} />
                    <span>{file.file_name}</span>
                </div>
            );
    }
};
