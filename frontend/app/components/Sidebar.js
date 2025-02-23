import React, { useEffect, useState } from 'react';
import { queryUsersHistory } from '../actions/query_user_history';
import { useAuth } from '../api/auth_context';
import { queryID } from '../actions/query_user';
import { redirect } from 'next/navigation';
import { deleteUsersHistory } from '../actions/delete_user_history';
import { usePathname } from 'next/navigation';


export default function Sidebar({ isCollapsed, toggleIsCollapsed }) {
  const { user, login } = useAuth();
  const [history, setHistory] = useState([]);
  const [refresh, setRefresh] = useState(false);
  const [hoveredPrompt, setHoveredPrompt] = useState(null);
  const [editOpenPromptId, setEditOpenPromptId] = useState(null);
  const currentUrl = usePathname();

  const toggleHover = (prompt_id) => {
    setHoveredPrompt(prompt_id);
  };

  const toggleEditMenu = (prompt_id, event) => {
    event.stopPropagation();
    setEditOpenPromptId(editOpenPromptId === prompt_id ? null : prompt_id);
  };

  const delete_history = async (prompt_id, refreshHistory, event) => {
    event.stopPropagation();
    const promptUrl = `/${prompt_id}`;

    deleteUsersHistory(prompt_id, refreshHistory)

    if (currentUrl === promptUrl) {
      redirect('/');
    }
  }

  function refreshHistory() {
    setRefresh(!refresh);
  }

  useEffect(() => {
    const fetchHistory = async () => {
      if (user) {
        const user_id = (await queryID(user.username)).user_id[0];
        const response = (await queryUsersHistory(user_id)).result;
        setHistory(response);
      }
    };
    fetchHistory();
  }, [refresh, user]);

  return (
    <div className={`h-screen bg-gray-100 p-4 ${isCollapsed ? 'w-14' : 'w-'} transition-all duration-300`}>
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
        <div className='w-full'>
          <button
            type='button'
            className='w-full flex justify-center align-middle items-center gap-x-2 py-2 bg-gray-200 rounded-xl hover:bg-gray-300 shadow-sm mb-4'
            onClick={() => window.location.href = '/'}
          >
            <img src='pen-to-square.svg' alt='Pen To Square Icon' height='26' width='26'/>
            <div className='pt-1 text-md text-gray-700 '>
              New Systematic Review
            </div>
          </button>
          {history.length > 0 && (
            <div className='border-t-2'>
              <div className='mt-2'>
                <ul>
                  {history.map(([prompt_id, user_input]) => (
                    <li key={prompt_id}>
                      <div
                        className='flex items-center justify-between p-2 hover:bg-gray-200 hover:rounded-xl cursor-pointer'
                        onMouseEnter={() => toggleHover(prompt_id)}
                        onMouseLeave={() => { toggleHover(null); setEditOpenPromptId(null); }}
                        onClick={() => redirect(`/${prompt_id}`)}
                      >
                        <span className='block w-full truncate'>
                          {user_input}
                        </span>
                        {hoveredPrompt === prompt_id && (
                          <div className='relative inline-block'>
                            <div
                              className='hover:bg-gray-300 hover:rounded-full'
                              onClick={(event) => toggleEditMenu(prompt_id, event)} // Pass event and stop propagation
                            >
                              <img src='ellipsis.svg' alt='Close Icon' height='20' width='20' className='flex-shrink-0 px-[2px] py-[1px] mr-[2px]' />
                            </div>
                            {editOpenPromptId === prompt_id && (
                              <div
                                className='absolute left-0 transform -translate-x-1 mt-2 rounded-md w-48 border z-50 bg-white ring-1 shadow-lg ring-black/5 focus:outline-hidden'
                                onMouseLeave={() => setEditOpenPromptId(null)}
                              >
                                <div className='py-1'>
                                  <button className='block w-full px-4 py-2 text-left text-sm text-gray-700 border-b-2 hover:bg-gray-50'>
                                    Change Name
                                  </button>
                                  <button 
                                    className='block w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50'
                                    onClick={(event) => delete_history(prompt_id, refreshHistory, event)}
                                  >
                                    Delete
                                  </button>
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}