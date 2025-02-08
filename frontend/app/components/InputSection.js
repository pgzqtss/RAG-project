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
    <div className='w-full h-full flex flex-col justify-center align-center items-center mt-[15%] bg-white overflow-y-auto'>
      <div>
        <p className=' text-2xl font-semibold text-gray-700 text-center mb-4 overflow-y-auto'>
          Ask a Research Question
        </p>
      </div>
      <div className='flex flex-auto w-[50%] min-w-[300pt]'>
        <form onSubmit={handleSubmit} className='w-full overflow-y-clip'>
          <TextArea 
            currentPrompt={currentPrompt} 
            setCurrentPrompt={setCurrentPrompt} 
            isAttachOpen={isAttachOpen}
            toggleAttachOpen={toggleAttachOpen}
            id={id}
          />
          <SubmitButton 
            isInputEmpty={isInputEmpty}
          />
        </form>
      </div>
    </div>
  );
}