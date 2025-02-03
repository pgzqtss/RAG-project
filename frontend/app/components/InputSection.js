import React, { useState, useEffect, useActionState } from 'react';
import TextArea from './TextArea';
import SubmitButton from './SubmitButton';
import { randomBytes } from 'crypto';
import { upsert } from '../actions/upsert';

export default function InputSection({ currentPrompt, setCurrentPrompt, isAttachOpen, toggleAttachOpen }) {
  const [id, setId] = useState(null);

  useEffect(() => {
    setId(parseInt(randomBytes(4).toString('hex'), 16))
  }, [])

  const handleSubmit = (e) => {
    e.preventDefault();
    upsert(id);
    console.log('Prompt submitted:', currentPrompt);
    setCurrentPrompt('');
  };

  console.log(id)
  return (
    <div className='w-full min-h-screen flex flex-col justify-center items-center bg-white'>
      <div>
        <p className='text-2xl font-semibold text-gray-700 text-center mb-4'>
          Ask a Research Question
        </p>
      </div>
      <div className='flex w-full max-w-2xl pb-32'>
        <form onSubmit={ handleSubmit } className='w-full'>
          <TextArea 
            currentPrompt={currentPrompt} 
            setCurrentPrompt={setCurrentPrompt} 
            isAttachOpen={isAttachOpen}
            toggleAttachOpen={toggleAttachOpen}
            id={id}
          />
          <SubmitButton 
          />
        </form>
      </div>
    </div>
  );
}