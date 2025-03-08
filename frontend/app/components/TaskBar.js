import { useState, useEffect } from 'react';
import fetchFiles from '../api/fetch_files_api';

export default function TaskBar({ id }) {
  const [files, setFiles] = useState([]);
  const [showFiles, setShowFiles] = useState(false)
  const [refresh, setRefresh] = useState(false)

  useEffect(() => {
      fetchFiles({ id, setFiles });
    }, [refresh]);

  return(
    <div className='flex flex-col w-full'>
      <div className='flex flex-row w-full'>
        <div className='flex w-full justify-start'>
          <button 
            className='text-sm px-4 p-2 mb-2 rounded-xl bg-gray-100 hover:bg-gray-200 transition hover:scale-105'
            onClick={() => {setShowFiles(!showFiles); setRefresh(!refresh); }}
          >
            <div className='flex justify-center gap-x-2'>
              <span>Show Files</span>
              <img src={`${showFiles ? 'angle-down.svg' : 'angle-up.svg'}`} alt='Dropdown Icon' height='16' width='16'></img>
            </div>
          </button>
        </div>
        <div className='flex w-full justify-end gap-x-2'>
          <a
            href={`output/${id}/systematic_review.pdf`}
            className='text-sm p-2 mb-2 rounded-xl bg-gray-100 hover:bg-gray-200 transition hover:scale-105'
            target='_blank' rel='noopener noreferrer'
          >
            <div className='flex justify-center gap-x-2 px-2'>
              <span>Export as PDF</span>
              <img src='arrow-up-from-bracket.svg' alt='Export Icon' height='14' width='14'></img>
            </div>
          </a>
          <a 
            href={`output/${id}/quality_check_report.pdf`}
            className='text-sm p-2 mb-2 rounded-xl bg-gray-100 hover:bg-gray-200 transition hover:scale-105'
            target='_blank' rel='noopener noreferrer'
          >
            <div className='flex justify-center gap-x-2 px-2'>
              <span>Quality Check</span>
              <img src='check.svg' alt='Dropdown Icon' height='16' width='16'></img>
            </div>
          </a>
        </div>
      </div>
      <div className={`${showFiles ? 'bg-gray-50 p-2 rounded-2xl mb-2' : ''}`}>
        {showFiles && files != undefined && files.length > 0 && (
          <ul className='grid grid-cols-6 gap-2 max-h-[90px] overflow-auto'>
            {files.map((file, index) => (
              <li key={index} className='col-span-1'>
                <a href={`files/${id}/${file}`} target='_blank' rel='noopener noreferrer' className='w-full'>
                  <div
                    className='flex items-center justify-between w-full bg-gray-100 border-[1px] border-gray-200 rounded-xl py-1 px-2 hover:bg-gray-200 gap-y-2'
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