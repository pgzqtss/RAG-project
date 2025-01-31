import { loginUser } from '../lib/api';

export async function login(state, formData) {
    const username = formData.get('username');
    const password = formData.get('password');

    try {
        const response = await loginUser(username, password);
        
        if (response.error) {
            return {
                errors: response.error
            }
        }

        return {
            message: 'Login successful'
        }
    } catch (error) {
        console.error('Error occured with log in', error)
        return {
            errors: 'An error occured with log in'
        }
    }
}