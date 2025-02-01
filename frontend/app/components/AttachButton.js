import React from 'react';
import AttachPopup from './AttachPopup';

export default function AttachButton({ isAttachOpen, toggleAttachOpen }) {
  return (
    <div className='flex justify-start mt-2'>
      <button
        type='button'
        className='bg-gray-200 text-white py-2 px-3 rounded-xl hover:bg-gray-300 focus:outline-none focus:ring-2'
        onClick={toggleAttachOpen}
      >
        <div className='flex align-middle'>
          <div className='text-gray-700 pr-2'>Attach Papers</div>
          <div className='flex align-middle'>
            <img src='paperclip.svg' alt='Paperclip Icon' height='18' width='18' />
          </div>
        </div>
      </button>
      <AttachPopup 
        isAttachOpen={isAttachOpen}
        toggleAttachOpen={toggleAttachOpen}
      />
    </div>
  );
}