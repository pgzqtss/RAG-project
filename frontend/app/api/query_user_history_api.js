export async function queryUserHistory(user_id) {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/query_user_history', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ user_id })
    });

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error searching user history:', error);
  }
}