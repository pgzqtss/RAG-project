export async function upsertVectors(id) {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/upsert', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ id })
    });

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error upserting vectors:', error);
    if (typeof window !== 'undefined') {
      redirect('/500')
    }
  }
}