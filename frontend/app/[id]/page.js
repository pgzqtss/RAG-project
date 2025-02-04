'use client';

import React, { lazy, Suspense, use, useState, useEffect } from 'react';
import '../globals.css';
import { useSearchParams } from 'next/navigation';
import { upsert } from '../actions/upsert';
import { generate } from '../actions/generate';
import UpsertLoading from '../components/UpsertLoading';
import GenerateLoading from '../components/GenerateLoading';

export default function Page({ params }) {
  const resolvedParams = use(params);
  const id = resolvedParams.id;

  const searchParams = useSearchParams();
  const prompt = searchParams.get('prompt');

  const [isUpsertLoading, setUpsertLoading] = useState(false);
  const [isGenerateLoading, setGenerateLoading] = useState(false);
  const [upsertResponse, setUpsertResponse] = useState('');
  const [generateResponse, setGenerateResponse] = useState('');

  useEffect(() => {
    async function fetchData() {
      setUpsertLoading(true);
      try {
        const upsertRes = await upsert(id, prompt);
        setUpsertResponse(upsertRes.message);
      } catch (error) {
        console.error('Upsert failed:', error);
        setUpsertResponse('Error during upsert');
      }
      setUpsertLoading(false);

      setGenerateLoading(true);
      try {
        const generateRes = await generate(id);
        setGenerateResponse(generateRes.message);
      } catch (error) {
        console.error('Generation failed:', error);
        setGenerateResponse('Error during generation.');
      }
      setGenerateLoading(false);
    }

    fetchData();
  }, [id, prompt]);

  return (
    <div>
      <p>{id}</p>
      <p>{prompt}</p>

      {isUpsertLoading ? <UpsertLoading /> : <p>Upsert Result: {upsertResponse}</p>}

      {isGenerateLoading ? <GenerateLoading /> : <p>Generate Result: {generateResponse}</p>}
    </div>
  );
}