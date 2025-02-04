import React, { useState } from 'react';
import LoginPopup from './LoginPopup';
import SignupPopup from './SignupPopup';
import { useAuth } from '../api/auth_context';

export default function UserProfile({ toggleLoginOpen, isLoginOpen, toggleSignupOpen, isSignupOpen }) {
  const { user, logout } = useAuth();
  const [isMenuOpen, setMenuOpen] = useState(false);

  console.log(isMenuOpen)

  const toggleMenuOpen = () => { setMenuOpen(!isMenuOpen); }

  return (
    <div className='flex justify-end w-full'>
      {user ? (
        <div className='flex items-center'>
          <button
            type='button'
            onClick={toggleMenuOpen}
          >
            <div className='flex justify-end items-center bg-gray-200 hover:bg-gray-300 rounded-full'>
              <div className='p-3'>
                <img src='user.svg' alt='User Icon' height='16' width='16' />
              </div>
              <div className='flex gap-x-2 font-medium text-lg mr-4'>
                {user.username}
                <img src='angle-down.svg' alt='Dropdown Arrow' height='16' width='16'></img>
              </div>
            </div>
          </button>
          {isMenuOpen && (
            <div className='absolute right-0 z-10 mt-[80pt] mr-4 w-48 origin-top-right rounded-md bg-white ring-1 shadow-lg ring-black/5 focus:outline-hidden hover:bg-gray-50'>
              <div className='py-1'>
                <button
                  type='button'
                  onClick={logout}
                  className='block w-full px-4 py-2 text-left text-sm text-gray-700'
                >
                  Log Out
                </button>
              </div>
            </div>
          )}
        </div>
      ) : (
        <button
          type='button'
          onClick={() => {setMenuOpen(false);toggleLoginOpen();}}
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
      )}
      <LoginPopup
        toggleLoginOpen={toggleLoginOpen}
        isLoginOpen={isLoginOpen}
        toggleSignupOpen={toggleSignupOpen}
        isSignupOpen={isSignupOpen}
      />
      <SignupPopup
        toggleSignupOpen={toggleSignupOpen}
        isSignupOpen={isSignupOpen}
        toggleLoginOpen={toggleLoginOpen}
        isLoginOpen={isLoginOpen}
      />
    </div>
  );
}