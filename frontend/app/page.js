'use client'

import React from 'react';
import './globals.css';
import { useState } from 'react';

function Header({ toggleLoginOpen, isLoginOpen, toggleSignUp, isSignUp }) {
  return (
    <div className='w-full'>
      <div className='flex items-center'>
        <h1 className='w-full text-2xl font-semibold text-gray-700'>Rag-n-Bones</h1>
        <UserProfile 
          toggleLoginOpen={toggleLoginOpen}
          isLoginOpen={isLoginOpen}
          toggleSignUp={toggleSignUp}
          isSignUp={isSignUp}
        />
      </div>
    </div>
  );
}

function UserProfile({ toggleLoginOpen, isLoginOpen, toggleSignUp, isSignUp }) {
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
        toggleSignUp={toggleSignUp}
      />
      <SignUpPopup
        toggleSignUp={toggleSignUp}
        isSignUp={isSignUp}
        toggleLoginOpen={toggleLoginOpen}
      />
    </div>
  );
}

function LoginPopup({ toggleLoginOpen, isLoginOpen, toggleSignUp }) {
  return (
    <div>
      {isLoginOpen && (
        <div className='fixed inset-0 flex items-center justify-center'>
          <div className='absolute inset-0 bg-black opacity-50'
          >
          </div>
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
            <form onSubmit={toggleLoginOpen} className='space-y-4'>
              <div>
                <label htmlFor='email' className='block text-gray-700 mb-2'>
                  Email Address
                </label>
                <input
                  type='email'
                  id='email'
                  placeholder='Enter your email'
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
                  placeholder='Enter your password'
                  className='w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400'
                  required
                />
              </div>
              <button
                type='submit'
                className='w-full bg-gray-300 text-gray-700 py-2 rounded-lg hover:bg-gray-400 focus:outline-none'
                onClick={toggleLoginOpen}
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
                onClick={() => { toggleLoginOpen(); toggleSignUp(); }}
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

function SignUpPopup({isSignUp, toggleSignUp, toggleLoginOpen}) {
  return (
    <div>
      {isSignUp && (
        <div className='fixed inset-0 flex items-center justify-center'>
          <div className='absolute inset-0 bg-black opacity-50'
          >
          </div>
          <div className='relative bg-white p-6 rounded-lg shadow-lg w-96'>
            <div className='flex items-center'>
              <h2 className='w-full text-lg font-bold mb-4 '>Sign Up</h2>
              <button 
                onClick={toggleSignUp}
                className='flex justify-end pb-4 transition duration-300 ease-in-out hover:scale-110'
              >
                <img src='xmark.svg' alt='Close Icon' height='20' width='20'></img>
              </button>
            </div>
            <form onSubmit={toggleLoginOpen} className='space-y-4'>
              <div>
                <label htmlFor='email' className='block text-gray-700 mb-2'>
                  Email Address
                </label>
                <input
                  type='email'
                  id='email'
                  placeholder='e.g. john.doe@email.com'
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
                  placeholder='Enter your password'
                  className='w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400'
                  required
                />
              </div>
              <div>
                <label htmlFor='confirmPassword' className='block text-gray-700 mb-2'>
                  Confirm Password
                </label>
                <input
                  type='password'
                  id='password'
                  placeholder='Enter your password'
                  className='w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400'
                  required
                />
              </div>
              <button
                type='submit'
                className='w-full bg-gray-300 text-gray-700 py-2 rounded-lg hover:bg-gray-400 focus:outline-none'
              >
                Sign Up
              </button>
            </form>
            <div className='flex w-full justify-center mt-4 gap-x-2'>
              <div className='items-center text-sm'>
                Already have an account?
              </div>
              <button
                className='text-sm text-blue-400 hover:underline focus:outline-none'
                onClick={() => { toggleLoginOpen(); toggleSignUp(); }}
              >
                Log In
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function InputSection({ currentPrompt, setCurrentPrompt, handleSubmit, isAttachOpen, toggleAttachOpen }) {
  return (
    <div className='w-full min-h-screen flex flex-col justify-center items-center bg-white'>
      <div>
        <p className='text-2xl font-semibold text-gray-700 text-center mb-4'>
          Ask a Research Question
        </p>
      </div>
      <div className='flex w-full max-w-2xl pb-32'>
        <form onSubmit={handleSubmit} className='w-full'>
          <TextArea 
            currentPrompt={currentPrompt} 
            setCurrentPrompt={setCurrentPrompt} 
            isAttachOpen={isAttachOpen}
            toggleAttachOpen={toggleAttachOpen}
          />
          <SubmitButton />
        </form>
      </div>
    </div>
  );
}

function TextArea({ currentPrompt, setCurrentPrompt, isAttachOpen, toggleAttachOpen }) {
  return (
    <div className='w-full h-28 p-3 border-white bg-gray-100 rounded-2xl flex flex-col justify-between'>
      <textarea
        value={currentPrompt}
        onChange={(e) => setCurrentPrompt(e.target.value)}
        placeholder='Type your research question here...'
        className='w-full h-2/3 bg-transparent resize-none focus:outline-none placeholder-gray-400'
      />
      <AttachButton 
        isAttachOpen={isAttachOpen}
        toggleAttachOpen={toggleAttachOpen}
      />
    </div>
  );
}

function AttachButton({ isAttachOpen, toggleAttachOpen }) {
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

function AttachPopup({ isAttachOpen, toggleAttachOpen}) {
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

function SubmitButton() {
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

function InputPrompt() {
  const [currentPrompt, setCurrentPrompt] = useState('');
  const [isLoginOpen, setLoginOpen] = useState(false);
  const [isSignUp, setSignUp] = useState(false);
  const [isAttachOpen, setAttachOpen] = useState(false);

  const toggleLoginOpen = () => {
    setLoginOpen(!isLoginOpen);
  };

  const toggleSignUp = () => {
    setSignUp(!isSignUp);
  };

  const toggleAttachOpen = () => {
    setAttachOpen(!isAttachOpen);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Prompt submitted:', currentPrompt);
    setCurrentPrompt('');
  };

  return (
    <div className='flex justify-center flex-col items-center bg-white'>
      <Header
        toggleLoginOpen={toggleLoginOpen}
        isLoginOpen={isLoginOpen}
        toggleSignUp={toggleSignUp}
        isSignUp={isSignUp}
      />
      <InputSection
        currentPrompt={currentPrompt}
        setCurrentPrompt={setCurrentPrompt}
        handleSubmit={handleSubmit}
        isAttachOpen={isAttachOpen}
        toggleAttachOpen={toggleAttachOpen}
      />
    </div>
  );
}

function Sidebar({isCollapsed, toggleIsCollapsed}) {
  return (
    <div className={`h-screen bg-gray-100 p-4 ${isCollapsed ? 'w-14' : 'w-full'} transition-all duration-300`}>
      <div className='flex items-center justify-between w-full pt-1'>
          {!isCollapsed && (
            <div className='justify-start text-xl text-gray-700 font-semibold mb-4'>
                <h2>History</h2>
            </div>
          )}
          <div className='justify-end pb-4'>
              <button
                  className='self-end focus:outline-none transition-transform duration-300 ease-in-out hover:scale-110' 
                  onClick={toggleIsCollapsed}
              >
                  <img src={`${isCollapsed ? 'angles-right.svg' : 'angles-left.svg'}`} alt='Sidebar Button' height='24' width='24' />
              </button>
          </div>
      </div>
      {!isCollapsed && (
        <ul className='space-y-4'>
          <li className='text-gray-700'>
            Systematic Review Example 1
          </li>
          <li className='text-gray-700'>
            Systematic Review Example 2
          </li>
        </ul>
      )}
    </div>
  )
}

export default function App() {
  const [isCollapsed, setIsCollapsed] = useState(false)

  const toggleIsCollapsed = () => {
      setIsCollapsed(!isCollapsed);
    };

  return (
    <div className='flex flex-row overflow-hidden'>
      <div className={`transition-all duration-300 ${isCollapsed ? 'w-16' : 'min-w-[200pt]'}`}>
          <Sidebar 
            isCollapsed={isCollapsed}
            toggleIsCollapsed={toggleIsCollapsed}
            />
      </div>
      <div className="w-full bg-white p-4">
        <InputPrompt />
      </div>
    </div>
  );
}