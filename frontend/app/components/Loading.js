export default function Loading({ message }) {
  return (
    <div className='flex w-full mb-[40%] items-center justify-center overflow-y-hidden'>
      <div className='flex min-w-[200pt] h-full justify-center align-middle bg-gray-200 rounded-2xl p-6'>
        <div className='w-full flex justify-center gap-x-3'>
          <div className='flex text-lg font-semibold items-center'>
            {message}
          </div>
          <div className=''>
            <img src='loading-ring.svg' alt='Loading Icon' height='24' width='24'></img>
          </div>
        </div>
      </div>
    </div>
  )
}