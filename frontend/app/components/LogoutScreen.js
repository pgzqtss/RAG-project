'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function LogoutScreen({ onAnimationEnd }) {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false);
      onAnimationEnd();
    }, 1500);

    return () => clearTimeout(timer);
  }, [onAnimationEnd]);

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 1, scale: 1 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.8 }}
          transition={{ duration: 0.8 }}
          className="fixed inset-0 flex items-center justify-center bg-gray-50 z-50"
        >
          <div className="text-center">
            <motion.img 
              src="rag-icon.png" 
              alt="RAG Logo" 
              className="mx-auto mb-4"
              style={{ height: '100px', width: '100px' }}
              initial={{ scale: 1 }}
              animate={{ scale: 1.1 }}
              transition={{ duration: 0.8, ease: "easeInOut" }}
            />
            <motion.h1
              className="text-3xl font-bold text-gray-700"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.3 }}
            >
              Logging Out...
            </motion.h1>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
