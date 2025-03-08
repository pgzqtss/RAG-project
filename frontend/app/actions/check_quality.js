import { genQualityCheck } from '../api/quality_check_api';


export async function check_quality(prompt_id) {
  try {
      const response = await genQualityCheck(prompt_id);
  
      if (response.error) {
        return {
          error: response.error
        }
      }
  
      return {
        message: 'Quality check graphs have been made successfully',
        success: true
      }
    } catch (error) {
      console.error('Error during quality checking:', error);
      return {
        errors: 'An error occured during quality checking',
        success: false
      }
    }
}