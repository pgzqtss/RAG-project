import { queryHistory } from '../api/query_history_api';

export async function query(prompt_id) {
  try {
      const response = await queryHistory(prompt_id);
      console.log(response)
  
      if (response.error) {
        return {
          error: response.error,
          success: false
        }
      }
  
      return {
        message: 'Systematic review was found successfully',
        prompt: response.prompt,
        systematic_review: response.systematic_review,
        success: true
      }
    } catch (error) {
      console.error('Error during query:', error);
      return {
        errors: 'An error occured during query',error ,
        success: false
      }
    }
}