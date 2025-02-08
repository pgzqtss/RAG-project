import React from 'react';
import AttachButton from './AttachButton';

export default function TextArea({ currentPrompt, setCurrentPrompt, isAttachOpen, toggleAttachOpen, isInputEmpty, id }) {
  return (
    <div className='w-full min-h-32 p-3 border-white bg-gray-100 rounded-2xl flex flex-col justify-between'>
  <textarea
    value={currentPrompt}
    onChange={(e) => {
      setCurrentPrompt(e.target.value);
      e.target.style.height = 'auto';
      e.target.style.height = e.target.scrollHeight + 'px'; 
    }}
    placeholder='Type your research question here...'
    className='w-full bg-transparent resize-none focus:outline-none placeholder-gray-400 text-lg overflow-hidden'
  />
  <div className='flex flex-row justify-between'>
    <AttachButton 
      isAttachOpen={isAttachOpen}
      toggleAttachOpen={toggleAttachOpen}
      isInputEmpty={isInputEmpty}
      id={id}
    />
  </div>
</div>
  );
}