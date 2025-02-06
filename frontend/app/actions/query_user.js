import { queryUser } from '../api/query_user_api';

export async function queryID(username) {
  try {
      const response = await queryUser(username);
      console.log(response)
  
      if (response.error) {
        return {
          error: response.error
        }
      }
  
      return {
        message: 'User was found successfully',
        user_id: response.user_id,
        success: true
      }
    } catch (error) {
      console.error('Error during query:', error);
      return {
        errors: 'An error occured during query',
        success: false
      }
    }
}