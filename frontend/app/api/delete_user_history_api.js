export async function deleteUserHistory(prompt_id) {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/delete_user_history', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ prompt_id })
    });

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error deleting systematic review:', error);
  }
}