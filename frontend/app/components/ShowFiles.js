import { useState, useEffect } from 'react';
import fetchFiles from '../api/fetch_files_api';

export default function ShowFiles({ id }) {
  const [files, setFiles] = useState([]);
  const [showFiles, setShowFiles] = useState(false)
  const [refresh, setRefresh] = useState(false)

  useEffect(() => {
      fetchFiles({ id, setFiles });
    }, [refresh]);

  return(
    <div className='flex flex-col w-full'>
      <div className='flex w-full justify-start'>
        <button 
          className='text-sm w-[120px] p-2 mb-2 rounded-xl bg-gray-100 hover:bg-gray-200 transition hover:scale-105'
          onClick={() => {setShowFiles(!showFiles); setRefresh(!refresh); }}
        >
          <div className='flex justify-center gap-x-2'>
            <span>Show Files</span>
            <img src={`${showFiles ? 'angle-down.svg' : 'angle-up.svg'}`} alt='Dropdown Icon' height='14' width='14'></img>
          </div>
        </button>
      </div>
      <div className={`${showFiles ? 'bg-gray-50 p-2 rounded-2xl mb-2' : ''}`}>
        {showFiles && files != undefined && files.length > 0 && (
          <ul className='grid grid-cols-6 gap-2 max-h-[90px] overflow-auto'>
            {files.map((file, index) => (
              <li key={index} className='col-span-1'>
                <a href={`files/${id}/${file}`} target='_blank' rel='noopener noreferrer'>
                  <div
                    className='flex items-center justify-between w-full bg-gray-100 border-[1px] border-gray-200 rounded-xl py-1 px-2 hover:bg-gray-200 mb-2'
                  >
                    <span className='text-sm overflow-hidden whitespace-nowrap text-ellipsis flex-1'>
                      {file}
                    </span>
                  </div>
                </a>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}