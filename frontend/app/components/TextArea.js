import React from 'react';
import AttachButton from './AttachButton';

export default function TextArea({ currentPrompt, setCurrentPrompt, isAttachOpen, toggleAttachOpen }) {
  return (
    <div className='w-full h-28 p-3 border-white bg-gray-100 rounded-2xl flex flex-col justify-between'>
      <textarea
        value={currentPrompt}
        onChange={(e) => setCurrentPrompt(e.target.value)}
        placeholder='Type your research question here...'
        className='w-full h-2/3 bg-transparent resize-none focus:outline-none placeholder-gray-400'
      />
      <AttachButton 
        isAttachOpen={isAttachOpen}
        toggleAttachOpen={toggleAttachOpen}
      />
    </div>
  );
}