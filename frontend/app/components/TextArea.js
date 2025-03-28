import React from 'react';
import AttachButton from './AttachButton';
import './TextArea.css'; 

export default function TextArea({ currentPrompt, setCurrentPrompt, isAttachOpen, toggleAttachOpen, isInputEmpty, id }) {
  return (
    <div className='textarea-wrapper'>
      <textarea
        value={currentPrompt}
        onChange={(e) => {
          setCurrentPrompt(e.target.value);
          e.target.style.height = 'auto';
          e.target.style.height = e.target.scrollHeight + 'px';
        }}
        placeholder='Type your research question here...'
        className='textarea'
      />
      <div className='button-group'>
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
