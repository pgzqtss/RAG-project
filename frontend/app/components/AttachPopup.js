'use client';
import { useRef } from 'react';

export default function AttachPopup({isAttachOpen, toggleAttachOpen}) {
  const fileInput = useRef(null); 

  async function uploadFile(evt) {
    evt.preventDefault();

    const formData = new FormData();
    // Loop through all selected files and append them to the formData
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
      console.log(result);
    } catch (error) {
      console.error('Error uploading files:', error);
    }
  }


  return (
    <div>
      {isAttachOpen && (
        <div className='fixed inset-0 flex items-center justify-center'>
          <div className='absolute inset-0 bg-black opacity-50'></div>
          <div className='relative bg-white w-[500pt] rounded-lg shadow-lg p-4'>
            <h2>Upload PDFs</h2>
            <input
              type='file'
              accept='application/pdf'
              ref={fileInput}
              multiple
            />
            <button onClick={uploadFile}>Upload</button>
            <p>Hi</p>
            <button onClick={toggleAttachOpen}>Close</button>
          </div>
        </div>
      )}
    </div>
  );
}