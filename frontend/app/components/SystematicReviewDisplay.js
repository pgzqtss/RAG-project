import ReactMarkdown from 'react-markdown';
import remarkBreaks from 'remark-breaks';
import TaskBar from './TaskBar';

const preprocessText = (text) => {
  text = text.replace(/\n/gi,'\n\n')
  text = text.replace(/-/g, '')
  return text.replace(/(?<=\n)(?![*-])\n/gi, '&nbsp;\n');
};

export default function SystematicReview({ prompt, text, id }) {
  return (
    <div className='flex flex-col items-center justify-center w-full h-full p-4'> 
      <div className='font-bold text-2xl text-center mb-4'>
        {prompt}
      </div>
      <div className='w-[700px]'>
        <TaskBar id={id} />
      </div>
      <div className='w-[700px] h-full bg-gray-50 rounded-3xl overflow-auto'>
        <div className='text-md p-4'>
          <ReactMarkdown
            remarkPlugins={[remarkBreaks]}
            components={{
              h2: ({ children }) => <h2 className='text-2xl font-semibold'>{children}</h2>,
              h3: ({ children }) => <h3 className='text-xl font-semibold'>{children}</h3>,
              p: ({ children }) => <p>{children}</p>,
            }}
          >
            {preprocessText(text)}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  );
}