import React from 'react';
import AttachButton from './AttachButton';

export default function TextArea({ currentPrompt, setCurrentPrompt, isAttachOpen, toggleAttachOpen, id }) {
  return (
    <div className='w-full min-h-32 p-3 border-white bg-gray-100 rounded-2xl flex flex-col justify-between'>
      <textarea
        value={currentPrompt}
        onChange={(e) => setCurrentPrompt(e.target.value)}
        placeholder='Type your research question here...'
        className='w-full h-2/3 bg-transparent resize-none focus:outline-none placeholder-gray-400 text-lg'
      />
      <AttachButton 
        isAttachOpen={isAttachOpen}
        toggleAttachOpen={toggleAttachOpen}
        id={id}
      />
    </div>
  );
}