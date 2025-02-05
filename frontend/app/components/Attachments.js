import React, { useEffect, useState, useRef } from 'react';

export default function Attachments({ id, refresh }) {
  const [files, setFiles] = useState([]);
  const isFirstRender = useRef(true)

  async function fetchFiles() {
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
  
  useEffect(() => {
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }

    fetchFiles();
  }, [refresh]);

  return (
    <div>
      {files.length > 0 && (
        <ul>
          {files.map((file, index) => (
            <li key={index}>
              <a href={`/files/${id}/${file}`} target="_blank" rel="noopener noreferrer">
                {file}
              </a>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}