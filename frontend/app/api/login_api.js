export async function loginUser(username, password) {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });

    const data = await response.json();

    return data;
  } catch (error) {
    console.error('Error logging in:', error);
  }
}