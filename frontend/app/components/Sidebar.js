import { redirect } from 'next/dist/server/api-utils';
import React from 'react';

export default function Sidebar({ isCollapsed, toggleIsCollapsed }) {
  return (
    <div className={`h-screen bg-gray-100 p-4 ${isCollapsed ? 'w-14' : 'w-full'} transition-all duration-300`}>
      <div className='flex items-center justify-between w-full pt-1'>
        {!isCollapsed && (
          <div className='justify-start text-xl text-gray-700 font-semibold mb-4'>
            <h1 className='w-full text-2xl font-semibold text-gray-700'>Rag-n-Bones</h1>
          </div>
        )}
        <div className='justify-end pb-4'>
          <button
            className='self-end focus:outline-none transition-transform duration-300 ease-in-out hover:scale-110' 
            onClick={toggleIsCollapsed}
          >
            <img src={`${isCollapsed ? 'angles-right.svg' : 'angles-left.svg'}`} alt='Sidebar Button' height='24' width='24' />
          </button>
        </div>
      </div>
      {!isCollapsed && (
        <button
          type='button'
          className='w-full flex justify-center align-middle items-center gap-x-2 py-2 bg-gray-200 rounded-xl hover:bg-gray-300 shadow-sm'
          onClick={() => window.location.href = '/'}
        >
          <img src='pen-to-square.svg' alt='Pen To Square Icon' height='26' width='26'/>
          <div className='pt-1 text-md text-gray-700'>
            New Systematic Review
          </div>
        </button>
      )}
    </div>
  );
}