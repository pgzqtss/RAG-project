import React from 'react';
import UserProfile from './UserProfile';

export default function Header({ toggleLoginOpen, isLoginOpen }) {
  return (
    <div className='w-full'>
      <div className='flex items-center'>
        <h1 className='w-full text-2xl font-semibold text-gray-700'>Rag-n-Bones</h1>
        <UserProfile 
          toggleLoginOpen={toggleLoginOpen}
          isLoginOpen={isLoginOpen}
        />
      </div>
    </div>
  );
}