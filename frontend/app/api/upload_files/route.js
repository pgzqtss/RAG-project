import { NextResponse } from 'next/server';
import { revalidatePath } from 'next/cache';
import fs from 'node:fs/promises';
import path from 'path';

export async function POST(req) {
  try {
    const formData = await req.formData();
    const files = formData.getAll('files'); // Get all files

    if (!files || files.length === 0) {
      return NextResponse.json({ status: 'fail', error: 'No files received' }, { status: 400 });
    }

    const uploadDir = path.join(process.cwd(), 'public/files');
    await fs.mkdir(uploadDir, { recursive: true });

    const uploadedFiles = [];

    for (const file of files) {
      const arrayBuffer = await file.arrayBuffer();
      const buffer = new Uint8Array(arrayBuffer);
      const filePath = path.join(uploadDir, file.name);

      await fs.writeFile(filePath, buffer);
      uploadedFiles.push({ filename: file.name, path: `/files/${file.name}` });
    }

    revalidatePath('/');

    return NextResponse.json({ status: 'success', files: uploadedFiles });
  } catch (e) {
    console.error(e);
    return NextResponse.json({ status: 'fail', error: e.message }, { status: 500 });
  }
}