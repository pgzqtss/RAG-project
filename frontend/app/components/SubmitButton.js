import React from 'react';

export default function SubmitButton({ isInputEmpty }) {
  return (
    <div className='flex justify-end my-2 gap-x-2'>
      <button
        type={`${isInputEmpty ? 'reset' : 'submit'}`}
        className='px-4 bg-gray-200 text-gray-700 py-2 rounded-xl hover:bg-gray-300 focus:outline-none focus:ring-2'
      >
        Generate
      </button>
    </div>
  );
}