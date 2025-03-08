export async function genQualityCheck(id) {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/quality_check', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ id })
    });

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error generating quality check graphs:', error);
  }
}