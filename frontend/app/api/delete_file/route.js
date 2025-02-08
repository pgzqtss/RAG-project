import { NextResponse } from 'next/server';
import { revalidatePath } from 'next/cache';
import fs from 'node:fs/promises';
import path from 'path';

export async function POST(req) {
  try {
    console.log('huh')
    const formData = await req.formData();
    const id = formData.get('id')
    const file = formData.get('file')

    console.log(formData)

    if (!file) {
      return NextResponse.json({ status: 'Fail', error: 'No file name received' }, { status: 400 });
    }

    const deleteDir = path.join(process.cwd(), 'files', id);
    console.log(deleteDir)
    const filePath = path.join(deleteDir, file);
    await fs.unlink(filePath);
    
    const files = await fs.readdir(deleteDir);
    if (files.length === 0) {
      await fs.rmdir(deleteDir);
    }

    revalidatePath('/');

    return NextResponse.json({ status: 'Success', files: file });
  } catch (e) {
    console.error(e);
    return NextResponse.json({ status: 'Fail', error: e.message }, { status: 500 });
  }
}