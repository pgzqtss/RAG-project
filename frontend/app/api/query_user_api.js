export async function queryUser(username) {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/query_user', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ username })
    });

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error searching for user:', error);
  }
}