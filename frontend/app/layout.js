'use client';

import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import { AuthProvider } from './api/auth_context';

export default function Layout({ children }) {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isLoginOpen, setLoginOpen] = useState(false);
  const [isSignupOpen, setSignupOpen] = useState(false);

  const toggleIsCollapsed = () => setIsCollapsed(!isCollapsed);
  const toggleLoginOpen = () => setLoginOpen(!isLoginOpen);
  const toggleSignupOpen = () => setSignupOpen(!isSignupOpen);

  return (
    <html lang='en'>
      <body>
        <AuthProvider>
          <div className="flex flex-row max-h-screen">
            <div className={`transition-all duration-300 ${isCollapsed ? 'w-16' : 'w-[230pt]'}`}>
              <Sidebar 
                isCollapsed={isCollapsed} 
                toggleIsCollapsed={toggleIsCollapsed} 
              />
            </div>
            <div className="flex flex-col w-full bg-white p-4">
              <Header 
                toggleLoginOpen={toggleLoginOpen} 
                isLoginOpen={isLoginOpen}
                toggleSignupOpen={toggleSignupOpen}
                isSignupOpen={isSignupOpen} 
              />
              <main>{children}</main>
            </div>
          </div>
        </AuthProvider>
      </body>
    </html>
  );
}