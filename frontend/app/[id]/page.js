'use client';

import React, { use, useState, useEffect } from 'react';
import '../globals.css';
import { useSearchParams } from 'next/navigation';
import { upsert } from '../actions/upsert';
import { generate } from '../actions/generate';
import Loading from '../components/Loading';
import SystematicReview from '../components/SystematicReviewDisplay';

export default function Page({ params }) {
  const resolvedParams = use(params);
  const id = resolvedParams.id;

  const searchParams = useSearchParams();
  const prompt = searchParams.get('prompt');

  const [isUpsertLoading, setUpsertLoading] = useState(false);
  const [isGenerateLoading, setGenerateLoading] = useState(false);
  const [generateResponse, setGenerateResponse] = useState('');

  useEffect(() => {
    async function fetchData() {
      setUpsertLoading(true);
      try {
        await upsert(id, prompt);
      } catch (error) {
        console.error('Upsert failed:', error);
      }
      setUpsertLoading(false);

      setGenerateLoading(true);
      try {
        const generateRes = await generate(prompt, id);
        console.log(generateRes)
        setGenerateResponse(generateRes.systematic_review);
      } catch (error) {
        console.error('Generation failed:', error);
        setGenerateResponse('Error during generation.');
      }
      setGenerateLoading(false);
    }

    fetchData();
  }, [id, prompt]);

  return (
    <div className='h-full overflow-hidden'>
      {isUpsertLoading ? <Loading message='Upserting Vectors'/> : ''}
      {isGenerateLoading ? <Loading message='Generating Systematic Review' /> : ''}
      {!isUpsertLoading && !isGenerateLoading && (
        <SystematicReview 
          prompt={prompt}
          text={generateResponse}
        />
      )};
    </div>
  );
}