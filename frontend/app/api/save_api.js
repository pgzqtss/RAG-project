export async function saveSystematicReview(user_id, prompt_id, prompt, systematic_review) {
  try {
    if (Array.isArray(user_id)) {
      user_id = user_id.map(id => parseInt(id, 10));
    } else {
      user_id = [parseInt(user_id, 10)];
    }

    prompt_id = parseInt(prompt_id, 10);

    const response = await fetch('http://127.0.0.1:5000/api/save', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ user_id, prompt_id, prompt, systematic_review })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error saving systematic review:', error);
  }
}
