'use client'

import React, { useState } from 'react';
import './globals.css'
import Sidebar from './components/Sidebar';
import Input from './components/Input';
import { AuthProvider } from './api/auth_context';

function MainContent() {
  const [isCollapsed, setIsCollapsed] = useState(true);
  
  const toggleIsCollapsed = () => {
    setIsCollapsed(!isCollapsed);
  };

  return (
    <div className='flex flex-row overflow-hidden max-h-screen'>
      <div className={`transition-all duration-300 ${isCollapsed ? 'w-16' : 'w-[230pt]'}`}>
        <Sidebar 
          isCollapsed={isCollapsed}
          toggleIsCollapsed={toggleIsCollapsed}
        />
      </div>
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