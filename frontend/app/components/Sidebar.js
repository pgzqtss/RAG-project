import React from 'react';

export default function Sidebar({ isCollapsed, toggleIsCollapsed }) {
  return (
    <div className={`h-screen bg-gray-100 p-4 ${isCollapsed ? 'w-14' : 'w-full'} transition-all duration-300`}>
      <div className='flex items-center justify-between w-full pt-1'>
        {!isCollapsed && (
          <div className='justify-start text-xl text-gray-700 font-semibold mb-4'>
            <h2>History</h2>
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
        <ul className='space-y-4'>
          <li className='text-gray-700'>Systematic Review Example 1</li>
          <li className='text-gray-700'>Systematic Review Example 2</li>
        </ul>
      )}
    </div>
  );
}