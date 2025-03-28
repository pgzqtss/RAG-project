import { NextResponse } from 'next/server';
import { revalidatePath } from 'next/cache';
import fs from 'node:fs/promises';
import path from 'path';

const ALLOWED_MIME_TYPES = ['application/pdf'];

export async function POST(req) {
  try {
    const formData = await req.formData();
    const files = formData.getAll('files');
    const id = formData.get('id');

    if (!id || !/^[a-zA-Z0-9_-]+$/.test(id)) {
      return NextResponse.json(
        { status: 'Fail', error: 'Invalid ID format' },
        { status: 400 }
      );
    }

    if (!files || files.length === 0) {
      return NextResponse.json(
        { status: 'Fail', error: 'No files received' },
        { status: 400 }
      );
    }

    const baseDir = path.resolve(process.cwd(), 'public', 'files');
    const uploadDir = path.resolve(baseDir, id);
    
    if (!uploadDir.startsWith(baseDir)) {
      return NextResponse.json(
        { status: 'Fail', error: 'Invalid directory' },
        { status: 403 }
      );
    }

    await fs.mkdir(uploadDir, { recursive: true });

    const uploadedFiles = [];
    for (const file of files) {
      if (!ALLOWED_MIME_TYPES.includes(file.type)) {
        continue;
      }

      const sanitizedFilename = file.name.replace(/[^a-zA-Z0-9\-_.]/g, '_');
      const filePath = path.resolve(uploadDir, sanitizedFilename);

      if (await fs.access(filePath).then(() => true).catch(() => false)) {
        continue; 
      }

      const arrayBuffer = await file.arrayBuffer();
      const buffer = new Uint8Array(arrayBuffer);
      await fs.writeFile(filePath, buffer);
      uploadedFiles.push({ filename: sanitizedFilename }); 
    }

    revalidatePath('/');
    return NextResponse.json({ status: 'Success', files: uploadedFiles });
  } catch (e) {
    console.error('[Upload Error]', e);
    return NextResponse.json(
      { status: 'Fail', error: 'Internal server error' },
      { status: 500 }
    );
  }
}