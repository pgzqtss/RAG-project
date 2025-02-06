import { revalidatePath } from 'next/cache';
import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function POST(req) {
  try {
    const formData = await req.formData();
    const id = formData.get('id');

    const readDir = path.join(process.cwd(), 'public/files', id);
    const files = fs.readdirSync(readDir);

    if (files.length === 0) {
      return NextResponse.json({status: 'Null', error: 'No files in the directory'}, {status: 400});
    }

    revalidatePath('/')

    return NextResponse.json({status: 'Success', files: files})
  } catch (error) {
    console.error('Error occurred reading files:', error);
    return NextResponse.json({status: 'Fail', error: error.message}, {status: 500})
  }
}