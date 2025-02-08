import React, { useState } from 'react';
import InputSection from './InputSection';

export default function Input() {
  const [currentPrompt, setCurrentPrompt] = useState('');
  const [isAttachOpen, setAttachOpen] = useState(false);

  const toggleAttachOpen = () => {
    setAttachOpen(!isAttachOpen);
  };

  return (
    <div className='h-full bg-white overflow-hidden'>
      <InputSection
        currentPrompt={currentPrompt}
        setCurrentPrompt={setCurrentPrompt}
        isAttachOpen={isAttachOpen}
        toggleAttachOpen={toggleAttachOpen}
      />
    </div>
  );
}