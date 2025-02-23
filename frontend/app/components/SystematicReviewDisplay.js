import ReactMarkdown from 'react-markdown';
import remarkBreaks from 'remark-breaks';

const preprocessText = (text) => {
  text = text.replace(/\n/gi,'\n\n')
  return text.replace(/(?<=\n)(?![*-])\n/gi, "&nbsp;\n ");
};

export default function SystematicReview({ prompt, text }) {
  return (
    <div className='flex flex-col items-center justify-center w-full h-[calc(100vh-100px)] p-4'> 
      <div className='font-bold text-2xl text-center mb-4'>
        {prompt}
      </div>
      <div className='w-[700px] h-full bg-gray-50 rounded-3xl overflow-auto'>
        <div className='text-md p-4'>
          <ReactMarkdown 
            remarkPlugins={[remarkBreaks]}
            children={preprocessText(text)}
         / >
        </div>
      </div>
    </div>
  );
}