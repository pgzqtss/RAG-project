import { queryID } from './query_user';
import { save } from './save';
import { upsert } from './upsert';
import { generate } from './generate';
import { check_quality } from './check_quality';

export async function GetSystematicReview({ setUpsertLoading, setGenerateLoading, setQualityLoading, id, prompt, toggleUpdate, setGenerate }) {
  setUpsertLoading(true);
  try {
    await upsert(id);
  } catch (error) {
    console.error('Upsert failed:', error);
  }
  setUpsertLoading(false);

  setGenerateLoading(true);
  try {
    const generateRes = await generate(prompt, id);
    console.log(generateRes)
    const systematic_review = generateRes.systematic_review

    const username = JSON.parse(localStorage.getItem('user')).username
    console.log(username)
    const user_id = (await queryID(username)).user_id;
    await save(user_id, id, prompt, systematic_review);
  } catch (error) {
    console.error('Generation failed:', error);
  }
  setGenerateLoading(false);

  setQualityLoading(true);
  try {
    await check_quality(id);
    setQualityLoading(false);
    setGenerate(false);
    toggleUpdate();
  } catch (error) {
    console.error('Quality checking failed:', error);
  }
}
