import ShowFiles from './ShowFiles';

export default function SystematicReview({ prompt, text, id }) {
  return (
    <div className='flex flex-col items-center justify-center w-full h-full p-4'> 
      <div className='font-bold text-2xl text-center mb-4'>
        {prompt}
      </div>
      <ShowFiles id={id} />
      <div className='w-[700px] h-full flex-grow bg-gray-50 rounded-3xl overflow-auto'>
        <div className='text-xl p-4'>
          {text}
        </div>
      </div>
    </div>
  );
}

{/* <a href={`/files/${id}/${file}`} target='_blank' rel='noopener noreferrer'></a> */}