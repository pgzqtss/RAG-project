'use client'

import React from 'react';
import './globals.css'
import Input from './components/Input';
import { AuthProvider } from './api/auth_context';
import { useAuth } from './api/auth_context';
import Home from './components/HomePage';

function MainContent({ user }) {
  return (
    <div className='flex h-full overflow-hidden'>
      <div className='w-full h-full p-4'>
        {user? (
          <Input />
        ) : (
          <Home />
          )
        }
      </div>
    </div>
  );
}

export default function App() {
  const { user } = useAuth();
  console.log(user)

  return (
    <AuthProvider>
      <MainContent 
        user={user}
      />
    </AuthProvider>
  );
}