'use client';

import React, { useState, useEffect } from 'react';
import '../globals.css';
import { useSearchParams } from 'next/navigation';
import Loading from '../components/Loading';
import SystematicReview from '../components/SystematicReviewDisplay';
import { query } from '../actions/query_history';
import { GetSystematicReview } from '../actions/get_systematic_review';
import { use } from 'react';

export default function Page({ params }) {
  const resolvedParams = use(params);
  const id = resolvedParams.id;

  const searchParams = useSearchParams();
  const prompt = searchParams.get('prompt');

  const [isUpsertLoading, setUpsertLoading] = useState(false);
  const [isGenerateLoading, setGenerateLoading] = useState(false);
  const [displayText, setDisplayText] = useState(false);
  const [generate, setGenerate] = useState(false);
  const [input, setInput] = useState('');
  const [output, setOutput] = useState('');

  const toggleUpdate = () => setGenerate(prev => !prev);
  
  const fetchData = async () => {
    const response = await query(id);

    if (response?.success) {
      setDisplayText(true);
      const data = await query(id);
      setInput(data.prompt);
      setOutput(data.systematic_review);

    } else {
      setGenerate(true);
    }
  };

  useEffect(() => {
    const timeout = setTimeout(() => {
      fetchData();
    }, 500);

    return () => clearTimeout(timeout);
  }, []);

  useEffect(() => {
    if (!generate) return;

    const generateReview = async () => {
      await GetSystematicReview({
        setUpsertLoading,
        setGenerateLoading,
        id,
        prompt,
        toggleUpdate,
        setGenerate,
      });
      
      await fetchData();
    };
    
    generateReview();
  }, [generate]);

  return (
    <div className='flex flex-col h-full overflow-hidden'>
      {isUpsertLoading && <Loading message='Upserting Vectors' />}
      {isGenerateLoading && <Loading message='Generating Systematic Review' />}
      {displayText && <SystematicReview prompt={input} text={output} id={id} />}
    </div>
  );
}