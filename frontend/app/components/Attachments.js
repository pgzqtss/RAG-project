import React, { useEffect, useState, useRef } from 'react';
import fetchFiles from '../api/fetch_files_api';
import { deleteFile } from '../actions/delete_file';

export default function Attachments({ id, refresh, refreshFiles }) {
  const [files, setFiles] = useState([]);
  const [hoveredIndex, setHoveredIndex] = useState(null);

  const toggleHover = (index) => {
    setHoveredIndex(index);
  };

  useEffect(() => {
    fetchFiles({ id, setFiles });
  }, [refresh]);

  return (
    <div className={`${files ? 'pt-2 mt-2 border-t-2' : ''}`}>
      {files != undefined && files.length > 0 && (
        <ul className="grid grid-cols-6 gap-2">
          {files.map((file, index) => (
            <li key={index} className="col-span-1">
              <button className="w-full">
                <div
                  className="flex items-center justify-between w-full bg-gray-200 rounded-xl py-1 px-2 hover:bg-gray-300"
                  onMouseEnter={() => toggleHover(index)}
                  onMouseLeave={() => toggleHover(null)}
                  onClick={(event) => deleteFile(event, file, id, refreshFiles)}
                >
                  <span className="text-sm overflow-hidden whitespace-nowrap text-ellipsis flex-1">
                    {file}
                  </span>
                  {hoveredIndex === index && (
                    <img src="xmark.svg" alt="Close Icon" height="12" width="12" className="ml-[2px] flex-shrink-0" />
                  )}
                </div>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}