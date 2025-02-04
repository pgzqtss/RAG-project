import React, { useActionState, useEffect } from 'react';
import { login as LoginAction} from '../actions/login_auth';
import { useAuth } from '../api/auth_context';

export default function LoginPopup({ toggleLoginOpen, isLoginOpen, toggleSignupOpen, isSignupOpen }) {
  const [state, action, pending] = useActionState((state, formData) => LoginAction(state, formData, login), undefined);
  const { login } = useAuth();

  useEffect(() => {
    if (state?.success === true) {
      toggleLoginOpen(); 
      login(state.username);
    }
  }, [state]); 

  return (
    <div>
      {isLoginOpen && (
        <div className='fixed inset-0 flex items-center justify-center'>
          <div className='absolute inset-0 bg-black opacity-50'></div>
          <div className='relative bg-white p-6 rounded-lg shadow-lg w-96'>
            <div className='flex items-center'>
              <h2 className='w-full text-lg font-bold mb-4 '>Log In</h2>
              <button 
                onClick={toggleLoginOpen}
                className='flex justify-end pb-4 transition duration-300 ease-in-out hover:scale-110'
              >
                <img src='xmark.svg' alt='Close Icon' height='20' width='20'></img>
              </button>
            </div>
            {state?.errors && (
              <div className='flex py-2 mb-3 w-[80%] align-middle justify-center items-center rounded-lg border-red-200 border-opacity-50 border-2 bg-red-100 gap-x-2'>
                <img src='xmark.svg' alt='Check Mark' height='16' width='16'></img>
                Invalid username or password.
              </div>
            )}
            <form action={action} className='space-y-4'>
              <div>
                <label htmlFor='email' className='block text-gray-700 mb-2'>
                  Username
                </label>
                <input
                  type='text'
                  id='username'
                  name='username'
                  placeholder='Enter your username'
                  className='w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400'
                  required
                />
              </div>
              <div>
                <label htmlFor='password' className='block text-gray-700 mb-2'>
                  Password
                </label>
                <input
                  type='password'
                  id='password'
                  name='password'
                  placeholder='Enter your password'
                  className='w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400'
                  required
                />
              </div>
              <button
                type='submit'
                className='w-full bg-gray-300 text-gray-700 py-2 rounded-lg hover:bg-gray-400 focus:outline-none'
                disabled={pending}
              >
                Login
              </button>
            </form>
            <div className='flex w-full justify-center mt-4 gap-x-2'>
              <div className='items-center text-sm'>
                Need an account?
              </div>
              <button
                className='text-sm text-blue-400 hover:underline focus:outline-none'
                onClick={() => {toggleLoginOpen(); toggleSignupOpen();}}
              >
                Sign Up
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}