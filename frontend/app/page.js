'use client'

import React, { useState } from 'react';
import './globals.css'
import Sidebar from './components/Sidebar';
import Input from './components/Input';

export default function App() {
  const [isCollapsed, setIsCollapsed] = useState(true);

  const toggleIsCollapsed = () => {
    setIsCollapsed(!isCollapsed);
  };

  return (
    <div className='flex flex-row overflow-hidden'>
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