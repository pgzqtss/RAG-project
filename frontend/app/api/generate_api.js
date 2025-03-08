import { redirect } from 'next/dist/server/api-utils';

export async function generateText(prompt, id) {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ prompt, id })
    });

    const data = await response.json();

    return data;
  } catch (error) {
    console.error('Error generating systematic review:', error);
    if (typeof window !== 'undefined') {
      redirect('/500')
    }
  }
}