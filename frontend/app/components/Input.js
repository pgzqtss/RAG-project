import React, { useState } from 'react';
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

  return (
    <div className='flex justify-center flex-col items-center bg-white'>
      <InputSection
        currentPrompt={currentPrompt}
        setCurrentPrompt={setCurrentPrompt}
        isAttachOpen={isAttachOpen}
        toggleAttachOpen={toggleAttachOpen}
      />
    </div>
  );
}