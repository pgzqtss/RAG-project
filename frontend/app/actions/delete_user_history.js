import { deleteUserHistory } from '../api/delete_user_history_api';

export async function deleteUsersHistory(prompt_id, refreshHistory) {
  try {
      const response = await deleteUserHistory(prompt_id);
      refreshHistory();
  
      if (response.error) {
        return {
          error: response.error
        }
      }
  
      return {
        message: 'Systematic review has been deleted sucessfully',
        success: true
      }
    } catch (error) {
      console.error('Error during deleting:', error);
      return {
        errors: 'An error occured during systematic review deletion'
      }
    }
}