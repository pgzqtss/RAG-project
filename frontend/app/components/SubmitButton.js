import React from 'react';

export default function SubmitButton() {
  return (
    <div className='flex justify-end'>
      <button
        type='submit'
        className='my-2 px-4 bg-gray-200 text-gray-700 py-2 rounded-xl hover:bg-gray-300 focus:outline-none focus:ring-2'
      >
        Generate
      </button>
    </div>
  );
}