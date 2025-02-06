import { generateText } from '../api/generate_api'; 

export async function generate(prompt, id) {
  try {
      const response = await generateText(prompt, id);
      console.log('PIKA')
      console.log(response)
  
      if (response.error) {
        return {
          error: response.error
        }
      }
  
      return {
        systematic_review: response.systematic_review,
        message: 'Systematic review has been generated sucessfully',
        success: true
      }
    } catch (error) {
      console.error('Error during generating:', error);
      return {
        errors: 'An error occured during systematic review generation'
      }
    }
}