import React from 'react';
import UserProfile from './UserProfile';

export default function Header({ toggleLoginOpen, isLoginOpen, toggleSignupOpen, isSignupOpen }) {
  return (
    <div className='w-full'>
      <div className='flex items-center'>
        <UserProfile 
          toggleLoginOpen={toggleLoginOpen}
          isLoginOpen={isLoginOpen}
          toggleSignupOpen={toggleSignupOpen}
          isSignupOpen={isSignupOpen}
        />
      </div>
    </div>
  );
}