export async function uploadFile(event, fileInput, id, setMessage, refreshFiles, setLoading) {
  event.preventDefault();
  setLoading(true);

  const formData = new FormData();
  formData.append('id', id);

  if (fileInput.current && fileInput.current.files) {
    Array.from(fileInput.current.files).forEach((file) => {
      formData.append('files', file);
    });
  }

  try {
    const response = await fetch('/api/upload_files', {
      method: 'POST',
      body: formData,
    });

    const result = await response.json();
    setMessage(result.status === 'Success' ? "Upload successful." : "Upload failed.");
    console.log(result.status);
    setLoading(false);
    refreshFiles();

  } catch (error) {
    console.error('Error uploading files:', error);
    setMessage(error.message || 'Upload failed.');
  }
}