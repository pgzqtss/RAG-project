'use client';

import React, { useState, useEffect } from 'react';
import './globals.css';
import Input from './components/Input';
import { AuthProvider } from './api/auth_context';
import { useAuth } from './api/auth_context';
import Home from './components/HomePage';
import LogoutScreen from './components/LogoutScreen';
import LoggingInScreen from './components/LoggingInScreen'; 

function MainContent({ user }) {
  return (
    <div className='flex h-full overflow-hidden'>
      <div className='w-full h-full p-4'>
        {user ? (
          <Input />
        ) : (
          <Home />
        )}
      </div>
    </div>
  );
}

export default function App() {
  const { user, showLogout, showLogin } = useAuth(); 

  return (
    <AuthProvider>
      {showLogin && <LoggingInScreen />}  {/* Log in */} 
      {showLogout && <LogoutScreen />}    {/* Logout */}
      <MainContent user={user} />
    </AuthProvider>
  );
}
