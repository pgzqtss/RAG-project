import { upsertVectors } from '../api/upsert_api';

export async function upsert(id) {
  try {
      const response = await upsertVectors(id);
      console.log('FUCK')
      console.log(response)
  
      if (response.error) {
        return {
          error: response.error
        }
      }
  
      return {
        message: 'Files have been upserted successfully',
        success: true
      }
    } catch (error) {
      console.error('Error during upserting:', error);
      return {
        errors: 'An error occured during upserting'
      }
    }
}