// api/auth_context.js
import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [showLogout, setShowLogout] = useState(false);
  const [showLogin, setShowLogin] = useState(false); // 登录动画状态

  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }

    // 检查是否在登出状态
    const isLoggingOut = localStorage.getItem('isLoggingOut');
    if (isLoggingOut === 'true') {
      setShowLogout(true);
    }

    // 检查是否在登录状态
    const isLoggingIn = localStorage.getItem('isLoggingIn');
    if (isLoggingIn === 'true') {
      setShowLogin(true);
      setTimeout(() => {
        setShowLogin(false);
        localStorage.removeItem('isLoggingIn');
      }, 1500); // 登录动画持续时间
    }
  }, []);

  const login = (username) => {
    // 标记登录状态
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
