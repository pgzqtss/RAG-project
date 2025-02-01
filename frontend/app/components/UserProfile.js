import React from 'react';
import LoginPopup from './LoginPopup';

export default function UserProfile({ toggleLoginOpen, isLoginOpen }) {
  return (
    <div className='flex justify-end w-full'>
      <button
        type='button'
        onClick={toggleLoginOpen}
      >
        <div className='flex justify-end items-center bg-gray-200 hover:bg-gray-300 rounded-full'>
          <div className='p-3'>
            <img src='user.svg' alt='User Icon' height='16' width='16' />
          </div>
          <div className='font-medium text-lg mr-4'>
            Log In
          </div>
        </div>
      </button>
      <LoginPopup
        toggleLoginOpen={toggleLoginOpen}
        isLoginOpen={isLoginOpen}
      />
    </div>
  );
}