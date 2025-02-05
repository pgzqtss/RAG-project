export default function Loading({ message }) {
  return (
    <div className='flex w-full pt-[22%] items-center justify-center overflow-y-hidden'>
      <div className='flex min-w-[200pt] justify-center align-middle bg-gray-200 rounded-lg p-6'>
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