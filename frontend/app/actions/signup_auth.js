import { SignupSchema } from '../lib/schema'
import { registerUser } from '../api/register_api';
 
export async function signup(state, formData) {
  const username = formData.get('username');
  const password = formData.get('password');
  const confirmPassword = formData.get('confirmPassword')
  
  const validatedFields = SignupSchema.safeParse({
    username: username,
    password: password,
    confirmPassword: confirmPassword
  })
 
  if (!validatedFields.success) {
    return {
      errors: validatedFields.error.flatten().fieldErrors,
    }
  } 
  
  try {
    const response = await registerUser(username, password);
    console.log(response)

    if (response.error) {
      return {
        error: response.error
      }
    }

    return {
      message: 'Registration successful',
      success: true
    }
  } catch (error) {
    console.error('Error during registration:', error);
    return {
      errors: 'An error occured during registration'
    }
  }
}