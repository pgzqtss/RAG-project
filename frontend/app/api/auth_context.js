// api/auth_context.js
import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [showLogout, setShowLogout] = useState(false);
  const [showLogin, setShowLogin] = useState(false);

  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }

    const isLoggingOut = localStorage.getItem('isLoggingOut');
    if (isLoggingOut === 'true') {
      setShowLogout(true);
    }

    const isLoggingIn = localStorage.getItem('isLoggingIn');
    if (isLoggingIn === 'true') {
      setShowLogin(true);
      setTimeout(() => {
        setShowLogin(false);
        localStorage.removeItem('isLoggingIn');
      }, 1500); 
    }
  }, []);

  const login = (username) => {
    localStorage.setItem('isLoggingIn', 'true');
    setShowLogin(true);
    setTimeout(() => {
      setUser({ username });
      localStorage.setItem('user', JSON.stringify({ username }));
      setShowLogin(false);
      localStorage.removeItem('isLoggingIn');
    }, 1500); // 动画时长
  };

  const logout = () => {
    localStorage.setItem('isLoggingOut', 'true');
    setShowLogout(true);
    setUser(null);
    localStorage.removeItem('user');

    setTimeout(() => {
      localStorage.removeItem('isLoggingOut');
      setShowLogout(false); 
      window.location.href = '/';
    }, 1500); 
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, showLogout, showLogin }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
