import React, { useState } from 'react';
import Header from './Header';
import InputSection from './InputSection';

export default function Input() {
  const [currentPrompt, setCurrentPrompt] = useState('');
  const [isLoginOpen, setLoginOpen] = useState(false);
  const [isAttachOpen, setAttachOpen] = useState(false);

  const toggleLoginOpen = () => {
    setLoginOpen(!isLoginOpen);
  };

  const toggleAttachOpen = () => {
    setAttachOpen(!isAttachOpen);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Prompt submitted:', currentPrompt);
    setCurrentPrompt('');
  };

  return (
    <div className='flex justify-center flex-col items-center bg-white'>
      <Header
        toggleLoginOpen={toggleLoginOpen}
        isLoginOpen={isLoginOpen}
      />
      <InputSection
        currentPrompt={currentPrompt}
        setCurrentPrompt={setCurrentPrompt}
        handleSubmit={handleSubmit}
        isAttachOpen={isAttachOpen}
        toggleAttachOpen={toggleAttachOpen}
      />
    </div>
  );
}