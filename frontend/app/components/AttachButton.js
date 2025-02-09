import React, { useState } from 'react';
import AttachPopup from './AttachPopup';
import Attachments from './Attachments';
import SubmitButton from './SubmitButton';

export default function AttachButton({ isAttachOpen, toggleAttachOpen, isInputEmpty, id }) {
  const [refresh, setRefresh] = useState(false)

  function refreshFiles() {
    setRefresh(!refresh);
  }
  
  return (
    <div className="w-full">
      <div className="flex flex-row justify-between items-center w-full">
        <button
          type="button"
          className="flex items-center transition-all duration-100 hover:scale-105 bg-gray-200 text-white py-2 px-3 rounded-xl hover:bg-gray-300 focus:outline-none focus:ring-2"
          onClick={toggleAttachOpen}
        >
          <span className="text-gray-700 pr-2">Attach Papers</span>
          <img src="file-pdf.svg" alt="Paperclip Icon" height="22" width="22" />
        </button>
        <SubmitButton isInputEmpty={isInputEmpty} />
      </div>
  
      <AttachPopup
        isAttachOpen={isAttachOpen}
        toggleAttachOpen={toggleAttachOpen}
        id={id}
        refreshFiles={refreshFiles}
      />
  
      <div className="w-full">
        <Attachments id={id} refresh={refresh} refreshFiles={refreshFiles} />
      </div>
    </div>
  );
}