import { NextResponse } from 'next/server';
import { revalidatePath } from 'next/cache';
import fs from 'node:fs/promises';
import path from 'path';

export async function POST(req) {
  try {
    const formData = await req.formData();
    const id = formData.get('id');
    const file = formData.get('file');

    if (!id || !file || 
        !/^[a-zA-Z0-9_-]+$/.test(id) || 
        !/^[a-zA-Z0-9\-_.]+$/.test(file)) {
      return NextResponse.json(
        { status: 'Fail', error: 'Invalid parameters' },
        { status: 400 }
      );
    }

    const baseDir = path.resolve(process.cwd(), 'public', 'files');
    const deleteDir = path.resolve(baseDir, id);
    const filePath = path.resolve(deleteDir, file);

    if (!filePath.startsWith(deleteDir) || !deleteDir.startsWith(baseDir)) {
      return NextResponse.json(
        { status: 'Fail', error: 'Invalid path' },
        { status: 403 }
      );
    }

    try {
      await fs.access(filePath);
    } catch (error) {
      return NextResponse.json(
        { status: 'Fail', error: 'File not found' },
        { status: 404 }
      );
    }

    await fs.unlink(filePath);

    try {
      const remainingFiles = await fs.readdir(deleteDir);
      if (remainingFiles.length === 0) {
        await fs.rm(deleteDir, { recursive: true, force: true });
      }
    } catch (error) {
      console.warn('fail to delate', error);
    }

    revalidatePath('/');
    return NextResponse.json({ status: 'Success' });
  } catch (e) {
    console.error('[Delete Error]', e);
    return NextResponse.json(
      { status: 'Fail', error: 'Internal server error' },
      { status: 500 }
    );
  }
}