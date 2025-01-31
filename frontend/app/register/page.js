'use client'

import React, { useActionState, useEffect } from 'react'
import Link from 'next/link'
import '../globals.css'
import { signup } from '../actions/signup_auth'
import { useRouter } from 'next/navigation'

export default function SignUp() {
  const [state, action, pending] = useActionState(signup, undefined)
  const router = useRouter();
  console.log(state)

  useEffect(() => {
    if (state?.message === 'Registration successful') {
      router.push('/');
    }
  }, [state, router]);

  return (
    <div>
        <div className='fixed inset-0 flex items-center justify-center'>
          <div className='absolute inset-0 bg-black opacity-10'
          >
          </div>
          <div className='relative bg-white p-6 rounded-lg shadow-lg w-96'>
            <div className='flex items-center'>
              <h2 className='w-full text-lg font-bold mb-4 '>Sign Up</h2>
            </div>
            <form action={ action } className='space-y-4'>
              <div>
                <label htmlFor='username' className='block text-gray-700 mb-2'>
                  Username
                </label>
                <input
                  type='text'
                  id='username'
                  name='username'
                  placeholder='Enter your username'
                  className='w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400'
                  required
                />
              </div> 
              {state?.errors?.username && <p>{state.errors.username}</p>}
              <div>
                <label htmlFor='password' className='block text-gray-700 mb-2'>
                  Password
                </label>
                <input
                  type='password'
                  id='password'
                  name='password'
                  placeholder='Enter your password'
                  className='w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400'
                  required
                />
              </div>
              {state?.errors?.password && (
                <div>
                  <p>Password must:</p>
                  <ul>
                    {state.errors.password.map((error) => (
                      <li key={error}> {error}</li>
                    ))}
                  </ul>
                </div>
              )}
              <div>
                <label htmlFor='confirmPassword' className='block text-gray-700 mb-2'>
                  Confirm Password
                </label>
                <input
                  type='password'
                  id='confirmPassword'
                  name='confirmPassword'
                  placeholder='Confirm your password'
                  className='w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400'
                  required
                />
              </div>
              {state?.errors?.confirmPassword && (
                <div>
                  <ul>
                    {state.errors.confirmPassword.map((error) => (
                      <li key={error}>- {error}</li>
                    ))}
                  </ul>
                </div>
              )}
              <button
                disabled={ pending }
                type='submit'
                className='w-full bg-gray-300 text-gray-700 py-2 rounded-lg hover:bg-gray-400 focus:outline-none'
              >
                Sign Up
              </button>
            </form>
            {/* {message && <p className='text-lg font-semibold'>{message}</p>} */}
            <div className='flex w-full justify-center mt-4 gap-x-2'>
              <div className='items-center text-sm'>
                Already have an account?
              </div>
              <Link
                className='text-sm text-blue-400 hover:underline focus:outline-none'
                href='/'
              >
                Log In
              </Link>
            </div>
          </div>
        </div>
    </div>
  )
}