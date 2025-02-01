import React from 'react';
import TextArea from './TextArea';
import SubmitButton from './SubmitButton';

export default function InputSection({ currentPrompt, setCurrentPrompt, handleSubmit, isAttachOpen, toggleAttachOpen }) {
  return (
    <div className='w-full min-h-screen flex flex-col justify-center items-center bg-white'>
      <div>
        <p className='text-2xl font-semibold text-gray-700 text-center mb-4'>
          Ask a Research Question
        </p>
      </div>
      <div className='flex w-full max-w-2xl pb-32'>
        <form onSubmit={handleSubmit} className='w-full'>
          <TextArea 
            currentPrompt={currentPrompt} 
            setCurrentPrompt={setCurrentPrompt} 
            isAttachOpen={isAttachOpen}
            toggleAttachOpen={toggleAttachOpen}
          />
          <SubmitButton />
        </form>
      </div>
    </div>
  );
}