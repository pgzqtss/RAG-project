import React from 'react';

export default function AttachPopup({ isAttachOpen, toggleAttachOpen }) {
  return (
    <div>
      {isAttachOpen && (
        <div className='fixed inset-0 flex items-center justify-center'>
          <div className='absolute inset-0 bg-black opacity-50'></div>
          <div className='relative bg-white w-[500pt] rounded-lg shadow-lg p-4'>
            test
          </div>
        </div>
      )}
    </div>
  );
}