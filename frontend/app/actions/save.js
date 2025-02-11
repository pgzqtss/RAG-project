import { saveSystematicReview } from '../api/save_api';

export async function save(user_id, prompt_id, prompt, systematic_review) {
  try {
      const response = await saveSystematicReview(user_id, prompt_id, prompt, systematic_review);
      
      if (response.error) {
        return {
          error: response.error
        }
      }
  
      return {
        message: 'Systematic review has been saved successfully',
        success: true
      }
    } catch (error) {
      console.error('Error during saving:', error);
      return {
        errors: 'An error occured during saving'
      }
    }
}