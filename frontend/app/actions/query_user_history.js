import { queryUserHistory } from '../api/query_user_history_api';

export async function queryUsersHistory(user_id) {
  try {
      const response = await queryUserHistory(user_id);
  
      if (response.error) {
        return {
          error: response.error
        }
      }
  
      return {
        message: 'User history was found successfully',
        result: response.result,
        success: true
      }
    } catch (error) {
      console.error('Error during user history query:', error);
      return {
        errors: 'An error occured during user history query',
        success: false
      }
    }
}