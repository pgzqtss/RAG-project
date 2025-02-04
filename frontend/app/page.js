'use client'

import React from 'react';
import './globals.css'
import Input from './components/Input';
import { AuthProvider } from './api/auth_context';

function MainContent() {
  return (
    <div className='flex flex-row overflow-hidden max-h-screen'>
      <div className="w-full bg-white p-4">
        <Input />
      </div>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <MainContent />
    </AuthProvider>
  );
}