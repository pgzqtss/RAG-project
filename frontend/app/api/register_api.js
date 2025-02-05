export async function registerUser(username, password) {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });

    const data = await response.json();

    revalidatePath('/');
    
    return data;
  } catch (error) {
    console.error('Error registering user:', error);
  }
}