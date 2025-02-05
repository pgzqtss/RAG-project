import React, { useState } from 'react';
import AttachPopup from './AttachPopup';
import Attachments from './Attachments';

export default function AttachButton({ isAttachOpen, toggleAttachOpen, id }) {
  const [refresh, setRefresh] = useState(false)

  function refreshFiles() {
    setRefresh(!refresh);
  }
  
  return (
    <div className=''>
      <div className='flex justify-start mt-2 gap-y-2'>
        <button
          type='button'
          className='bg-gray-200 text-white py-2 px-3 rounded-xl hover:bg-gray-300 focus:outline-none focus:ring-2'
          onClick={toggleAttachOpen}
        >
          <div className='flex align-middle'>
            <div className='text-gray-700 pr-2'>Attach Papers</div>
            <div className='flex align-middle'>
              <img src='file-pdf.svg' alt='Paperclip Icon' height='22' width='22'/>
            </div>
          </div>
        </button>
        <AttachPopup 
          isAttachOpen={isAttachOpen}
          toggleAttachOpen={toggleAttachOpen}
          id={id}
          refreshFiles={refreshFiles}
        />
      </div>
      <div className=''>
        <Attachments 
          id={id}
          refresh={refresh}
        />
      </div>
    </div>
  );
}