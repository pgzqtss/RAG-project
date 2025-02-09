'use client'

import React from 'react';
import './globals.css'
import Input from './components/Input';
import { AuthProvider } from './api/auth_context';

function MainContent() {
  return (
    <div className='flex h-full overflow-hidden'>
      <div className='w-full h-full p-4'>
        <Input />
      </div>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <div>
        Note: You will need to sign up before generating. Will add logic to not allow generation if not logged in.
      </div>
      <MainContent />
    </AuthProvider>
  );
}