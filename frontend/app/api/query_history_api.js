export async function queryHistory(prompt_id) {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/query', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ prompt_id })
    });

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error searching for systematic review:', error);
  }
}