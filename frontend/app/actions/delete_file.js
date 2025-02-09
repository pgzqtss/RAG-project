export async function deleteFile(event, file, id, refreshFiles) {
  event.preventDefault();

  console.log(file)
  console.log(id)

  
  try {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('id', id);

    console.log(formData)
    const response = await fetch('/api/delete_file', {
      method: 'POST',
      body: formData,
    });

    const result = await response.json();
    console.log(result.status);
    refreshFiles();

  } catch (error) {
    console.error('Error deleting file:', error);
  }
}