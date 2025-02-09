export default async function fetchFiles({ id, setFiles }) {
  try {
    const formData = new FormData();
    formData.append('id', id);

    const response = await fetch(`/api/get_files/`, {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();
    setFiles(data.files);
  } catch (error) {
    console.error('Error fetching files:', error);
  }
}