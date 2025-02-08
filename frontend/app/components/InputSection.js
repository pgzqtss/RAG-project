import React, { useState, useEffect, useActionState, Suspense } from 'react';
import TextArea from './TextArea';
import SubmitButton from './SubmitButton';
import { randomBytes } from 'crypto';
import { useRouter } from 'next/navigation';

export default function InputSection({ currentPrompt, setCurrentPrompt, isAttachOpen, toggleAttachOpen }) {
  const [id, setId] = useState(null);
  const [isInputEmpty, setInputEmpty] = useState(true)
  const router = useRouter();

  useEffect(() => {
    setId(parseInt(randomBytes(4).toString('hex'), 16))
  }, [])

  useEffect(() => {
    currentPrompt == '' ? setInputEmpty(true) : setInputEmpty(false);
  }, [currentPrompt])
  
  const handleSubmit = (e) => {
    e.preventDefault();
    router.push(`/${id}?prompt=${encodeURIComponent(currentPrompt)}`);
  };


  return (
    <div className='w-full h-full flex flex-col justify-center items-center bg-white overflow-hidden'>
      <div className='flex flex-col justify-center items-center w-full'>
        <p className='text-2xl font-semibold text-gray-700 text-center mb-4'>
          Ask a Research Question
        </p>
        <div className='flex flex-auto w-[500pt] min-w-[300pt] max-w-[500pt] mb-[20%]'>
          <form onSubmit={handleSubmit} className='flex flex-grow w-full'>
            <TextArea 
              currentPrompt={currentPrompt} 
              setCurrentPrompt={setCurrentPrompt} 
              isAttachOpen={isAttachOpen}
              toggleAttachOpen={toggleAttachOpen}
              isInputEmpty={isInputEmpty}
              id={id}
            />
          </form>
        </div>
      </div>
    </div>
  );
}