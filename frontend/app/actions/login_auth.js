import { loginUser } from '../api/login_api';
import { useAuth } from '../api/auth_context';

export async function login(state, formData, login) {
	const username = formData.get('username');
	const password = formData.get('password');

	try {
		const response = await loginUser(username, password);
		
		if (response.error) {
			return {
				errors: response.error
			}
		}

		login(username);
		
		return {
			message: 'Login successful',
			username: username,
			success: true
		}
	} catch (error) {
		console.error('Error occured with log in', error)
		return {
			errors: 'An error occured with log in'
		}
	}
}