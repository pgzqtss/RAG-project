from services.pinecone_service import initialise_pinecone
from services.pdf_processing_service import process_and_store_all_pdfs
from flask import request, jsonify
from __main__ import app

@app.route('/api/upsert', methods=['POST'])
def init_pinecone():
  data = request.json
  id = data.get('id')

  try:
    initialise_pinecone()
    process_and_store_all_pdfs(id)
  except Exception as e:
    print(f"Error: {e}")
    return jsonify({'error': str(e)}), 500

  return jsonify({'message': 'PDFs have been upserted into Pinecone successfully'}), 200