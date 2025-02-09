export default function Home() {
  return (
    <div className='w-full h-full flex flex-col items-center justify-center'>
      <img src='rag-icon.png' alt='RAG Icon' height='200' width='200' className='m-4'></img>
      <div className='flex w-full font-bold text-3xl justify-center'>
        Welcome to Rag-n-Bones
      </div>
      <p className='text-lg mt-2'>Log in to start exploring research insights.</p>
      <p className='text-lg mb-[30%]'>Upload papers, ask questions, and generate systematic reviews powered by AI.</p>
    </div>
  )
}