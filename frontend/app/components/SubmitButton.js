import React from 'react';

export default function SubmitButton({ isInputEmpty }) {
  return (
    <div className='flex flex-row justify-end'>
      <button
        type={`${isInputEmpty ? 'reset' : 'submit'}`}
        className='w-full py-2 flex transition-all duration-100 hover:scale-105 flex-row justify-center items-center gap-x-2 px-4 bg-gray-200 text-gray-700 rounded-full hover:bg-gray-300 focus:outline-none focus:ring-2'
      >
        Send <img src='paper-plane.svg' alt='Paper Plane Icon' height='20' width='20'></img>
      </button>
    </div>
  );
}