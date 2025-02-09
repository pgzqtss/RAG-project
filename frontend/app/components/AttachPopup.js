'use client';
import { useRef, useState } from 'react';
import { uploadFile } from '../actions/upload_file';

export default function AttachPopup({ isAttachOpen, toggleAttachOpen, id, refreshFiles }) {
  const fileInput = useRef(null); 
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  // async function uploadFile(event) {
  //   event.preventDefault();

  //   const formData = new FormData();
  //   formData.append('id', id);

  //   if (fileInput.current && fileInput.current.files) {
  //     Array.from(fileInput.current.files).forEach((file) => {
  //       formData.append('files', file);
  //     });
  //   }

  //   try {
  //     const response = await fetch('/api/upload_files', {
  //       method: 'POST',
  //       body: formData,
  //     });

  //     const result = await response.json();
  //     setMessage(result.status === 'Success' ? "Upload successful." : "Upload failed.");
  //     console.log(result.status);
  //     refreshFiles();
  //   } catch (error) {
  //     console.error('Error uploading files:', error);
  //     setMessage(error.message || 'Upload failed.')
  //   }
  // }


  return (
    <div>
      {isAttachOpen && (
        <div className='fixed inset-0 flex items-center justify-center'>
          <div className='absolute inset-0 bg-black opacity-50'></div>
          <div className='relative bg-white w-[300pt] rounded-lg shadow-lg p-4'>
            <div className='flex items-center'>
              <h2 className='w-full text-lg font-bold mb-4'>Upload PDFs</h2>
              <button 
                onClick={() => { toggleAttachOpen(); setMessage(''); }}
                className='flex justify-end pb-4 transition duration-300 ease-in-out hover:scale-110'
              >
                <img src='xmark.svg' alt='Close Icon' height='20' width='20'></img>
              </button>
            </div>
            <div className='flex w-full'>
              <input
                type='file'
                accept='application/pdf'
                ref={fileInput}
                multiple
                className='flex w-full justify-start'
              />
            </div>
            <div className='flex w-full'>
              <div className='flex w-full items-end justify-start m-1'>
                <p className={`font-semibold text-sm ${message == 'Upload successful.' ? 'text-green-500' : 'text-red-500'}`}>{message}</p>
              </div>
              <div className='flex w-full items-center justify-end'>
                {loading && (
                  <>
                    <p className='flex justify-end font-semibold text-sm items-center'>Uploading...</p>
                    <img src='loading-ring.svg' alt='Loading Icon' height='20' width='20' className='mx-2'></img>
                  </>
                )}
                <button className='bg-gray-200 rounded-full shadow-sm px-4 py-2 text-gray-700 hover:bg-gray-300' 
                onClick={(event) => uploadFile(event, fileInput, id, setMessage, refreshFiles, setLoading)}>
                  Upload
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}