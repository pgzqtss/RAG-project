export async function saveSystematicReview(user_id, prompt_id, prompt, systematic_review) {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/save', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ user_id, prompt_id, prompt, systematic_review })
    });

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error saving systematic review:', error);
  }
}