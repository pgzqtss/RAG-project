import React from 'react';
import '../globals.css';
import Link from 'next/link';
import Head from 'next/head';

function Header() {
  return (
    <div className='flex w-full align-middle p-4'>
      <div className='absolute left-4 top-4'>
        <Link
          href='/'
          className='flex justify-start align-middle transition-all duration-300 ease-in-out hover:scale-110'
        >
          <img src='arrow-right-to-bracket.svg' alt='Back Icon' height='28' width='28'></img>
          <div className='flex justify-end ml-2 font-semibold text-lg'>
          Back
          </div>
        </Link>
      </div>
      <div className='flex w-full items-center justify-center font-semibold text-2xl text-gray-700'>Rag-n-Bones</div>
    </div>
  );
}

function SignUp() {
  return (
    <div></div>
  );
}

export default function CreateAccount() {
    return (
  
          <div className='w-full bg-gray-100'>
            <Header />
          </div>

    );
  }