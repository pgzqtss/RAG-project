export default function SystematicReview({ prompt, text }) {
  return (
    <div className='flex flex-col items-center justify-center w-full h-[calc(100vh-100px)] p-4'> 
      <div className='font-bold text-2xl text-center mb-4'>
        {prompt}
      </div>
      <div className='w-[700px] h-full  bg-gray-50 rounded-3xl overflow-auto'>
        <div className='text-xl p-4'>
          {text}
        </div>
      </div>
    </div>
  );
}