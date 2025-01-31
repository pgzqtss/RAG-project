import { z } from 'zod'
 
export const SignupSchema = z.object({
  username: z
    .string()
    .min(3, { message: 'Username must be at least 3 characters long.' })
    .trim(),
  password: z
    .string()
    .min(8, { message: 'Be at least 8 characters long' })
    .regex(/[A-Z]/, { message: 'Contain at least one capital letter.' })
    .regex(/[0-9]/, { message: 'Contain at least one number.' })
    .regex(/[^a-zA-Z0-9]/, {
      message: 'Contain at least one special character.',
    })
    .trim(),
  confirmPassword: z
    .string()
    .trim(),
}).refine((data) => data.password === data.confirmPassword, {
    message: 'Passwords much match',
    path: ['confirmPassword'],
  });