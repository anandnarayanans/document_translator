# import os
# from flask import Flask, request, jsonify, send_file, render_template
# from flask_cors import CORS, cross_origin
# import fitz  # PyMuPDF
# import pdfplumber
# import re
# import concurrent.futures
# from transformers import MBartForConditionalGeneration, MBart50TokenizerFast
# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas
# from time import sleep
# import tempfile

# app = Flask(__name__)
# CORS(app)

# def reverse_arabic_words(line):
#     arabic_word_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]+')
#     def reverse_arabic(match):
#         return match.group(0)[::-1]
#     return arabic_word_pattern.sub(reverse_arabic, line)

# def pdf_to_html_reverse_arabic(input_pdf, output_html):
#     with pdfplumber.open(input_pdf) as pdf:
#         lines = []
#         for page in pdf.pages:
#             text = page.extract_text()
#             if text:
#                 page_lines = text.split('\n')
#                 lines.extend(page_lines)

#     clean_lines = [re.sub(r'<.*?>', '', line) for line in lines]
#     processed_lines = [reverse_arabic_words(line) for line in clean_lines]

#     with open(output_html, 'w', encoding='utf-8') as html_file:
#         html_file.write('<html dir="rtl">\n<body>\n')
#         for line in processed_lines:
#             html_file.write(line.strip() + '<br>\n')
#         html_file.write('</body>\n</html>')

# def translate_arabic_to_english(model, tokenizer_name, line_ar):
#     tokenizer = MBart50TokenizerFast.from_pretrained(tokenizer_name)
#     tokenizer.src_lang = "ar_AR"
#     encoded_ar = tokenizer(line_ar, return_tensors="pt", max_length=1024, truncation=True)
#     generated_tokens = model.generate(**encoded_ar, forced_bos_token_id=tokenizer.lang_code_to_id["en_XX"])
#     trans = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
#     return trans[0]

# def write_to_pdf(translated_lines, file_path):
#     c = canvas.Canvas(file_path, pagesize=letter)
#     width, height = letter
#     y_position = height - 40

#     for line in translated_lines:
#         if y_position < 40:
#             c.showPage()
#             y_position = height - 40
#         c.drawString(40, y_position, line)
#         y_position -= 14

#     c.save()

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/upload', methods=['POST'])
# @cross_origin(origins=["http://localhost:4200"])
# def upload_file():
#     if 'file' not in request.files:
#         return jsonify({'error': 'No file part'}), 400

#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({'error': 'No selected file'}), 400

#     temp_dir = tempfile.gettempdir()
#     file_path = os.path.join(temp_dir, file.filename)
#     os.makedirs(temp_dir, exist_ok=True)  # Ensure the temporary directory exists
#     file.save(file_path)

#     return jsonify({'message': 'File uploaded successfully', 'file_path': file_path}), 200

# @app.route('/translate', methods=['POST'])
# @cross_origin(origins=["http://localhost:4200"])
# def translate():
#     input_pdf_path = request.json.get('file_path')
#     if not input_pdf_path or not os.path.exists(input_pdf_path):
#         return jsonify({'error': 'Invalid file path'}), 400

#     output_html_path = os.path.splitext(input_pdf_path)[0] + '.html'
#     pdf_to_html_reverse_arabic(input_pdf_path, output_html_path)

#     with open(output_html_path, 'r', encoding='utf-8') as html_file:
#         html_content = html_file.readlines()

#     model = MBartForConditionalGeneration.from_pretrained("facebook/mbart-large-50-many-to-many-mmt")
#     tokenizer_name = "facebook/mbart-large-50-many-to-many-mmt"

#     translated_lines = [None] * len(html_content)
#     with concurrent.futures.ThreadPoolExecutor() as executor:
#         future_to_index = {executor.submit(translate_arabic_to_english, model, tokenizer_name, line): idx for idx, line in enumerate(html_content)}
#         for future in concurrent.futures.as_completed(future_to_index):
#             idx = future_to_index[future]
#             translated_lines[idx] = future.result()

#     output_pdf_path = os.path.splitext(input_pdf_path)[0] + '_translated.pdf'
#     write_to_pdf(translated_lines, output_pdf_path)

#     return send_file(output_pdf_path, as_attachment=True, download_name='translated_file.pdf')

# if __name__ == '__main__':
#     app.run(debug=True)






# import os
# from flask import Flask, request, jsonify, send_file, render_template
# from flask_cors import CORS, cross_origin
# import pdfplumber
# import re
# import concurrent.futures
# from transformers import MarianMTModel, MarianTokenizer
# from fpdf import FPDF
# import tempfile

# app = Flask(__name__)
# CORS(app)

# def reverse_arabic_words(line):
#     arabic_word_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]+')
#     def reverse_arabic(match):
#         return match.group(0)[::-1]
#     return arabic_word_pattern.sub(reverse_arabic, line)

# def clean_text(line):
#     line = re.sub(r'[^\w\s]', '', line)  # Remove special characters
#     line = re.sub(r'\s+', ' ', line)  # Replace multiple spaces with a single space
#     return line.strip()

# def pdf_to_text_reverse_arabic(input_pdf):
#     with pdfplumber.open(input_pdf) as pdf:
#         lines = []
#         for page in pdf.pages:
#             text = page.extract_text()
#             if text:
#                 page_lines = text.split('\n')
#                 lines.extend(page_lines)
    
#     clean_lines = [clean_text(line) for line in lines]
#     processed_lines = [reverse_arabic_words(line) for line in clean_lines]
    
#     return processed_lines

# def translate_arabic_to_english(model, tokenizer, line_ar):
#     encoded_ar = tokenizer(line_ar, return_tensors="pt", max_length=1024, truncation=True)
#     generated_tokens = model.generate(**encoded_ar)
#     trans = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
#     return trans[0]

# def write_to_pdf(translated_lines, file_path):
#     pdf = FPDF()
#     pdf.add_page()
#     pdf.set_auto_page_break(auto=True, margin=15)
#     pdf.set_font("Arial", size=12)
    
#     for line in translated_lines:
#         pdf.multi_cell(0, 10, line)

#     pdf.output(file_path)

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/upload', methods=['POST'])
# @cross_origin(origins=["http://localhost:4200"])
# def upload_file():
#     if 'file' not in request.files:
#         return jsonify({'error': 'No file part'}), 400

#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({'error': 'No selected file'}), 400

#     temp_dir = tempfile.gettempdir()
#     file_path = os.path.join(temp_dir, file.filename)
#     os.makedirs(temp_dir, exist_ok=True)  # Ensure the temporary directory exists
#     file.save(file_path)

#     return jsonify({'message': 'File uploaded successfully', 'file_path': file_path}), 200

# @app.route('/translate', methods=['POST'])
# @cross_origin(origins=["http://localhost:4200"])
# def translate():
#     input_pdf_path = request.json.get('file_path')
#     if not input_pdf_path or not os.path.exists(input_pdf_path):
#         return jsonify({'error': 'Invalid file path'}), 400

#     lines = pdf_to_text_reverse_arabic(input_pdf_path)

#     model_name = "Helsinki-NLP/opus-mt-ar-en"
#     model = MarianMTModel.from_pretrained(model_name)
#     tokenizer = MarianTokenizer.from_pretrained(model_name)

#     translated_lines = [None] * len(lines)
#     with concurrent.futures.ThreadPoolExecutor() as executor:
#         future_to_index = {executor.submit(translate_arabic_to_english, model, tokenizer, line): idx for idx, line in enumerate(lines)}
#         for future in concurrent.futures.as_completed(future_to_index):
#             idx = future_to_index[future]
#             translated_lines[idx] = future.result()

#     output_pdf_path = os.path.splitext(input_pdf_path)[0] + '_translated.pdf'
#     write_to_pdf(translated_lines, output_pdf_path)

#     return send_file(output_pdf_path, as_attachment=True, download_name='translated_file.pdf')

# if __name__ == '__main__':
#     app.run(debug=True)






# progress bar
# import os
# from flask import Flask, request, jsonify, send_file, render_template, Response, stream_with_context
# from flask_cors import CORS, cross_origin
# import pdfplumber
# import re
# import concurrent.futures
# from transformers import MarianMTModel, MarianTokenizer
# from fpdf import FPDF
# import tempfile
# import json

# app = Flask(__name__)
# CORS(app)

# def reverse_arabic_words(line):
#     arabic_word_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]+')
#     def reverse_arabic(match):
#         return match.group(0)[::-1]
#     return arabic_word_pattern.sub(reverse_arabic, line)

# def clean_text(line):
#     line = re.sub(r'[^\w\s]', '', line)  # Remove special characters
#     line = re.sub(r'\s+', ' ', line)  # Replace multiple spaces with a single space
#     return line.strip()

# def pdf_to_text_reverse_arabic(input_pdf):
#     with pdfplumber.open(input_pdf) as pdf:
#         lines = []
#         for page in pdf.pages:
#             text = page.extract_text()
#             if text:
#                 page_lines = text.split('\n')
#                 lines.extend(page_lines)
    
#     clean_lines = [clean_text(line) for line in lines]
#     processed_lines = [reverse_arabic_words(line) for line in clean_lines]
    
#     return processed_lines

# def translate_arabic_to_english(model, tokenizer, line_ar):
#     encoded_ar = tokenizer(line_ar, return_tensors="pt", max_length=1024, truncation=True)
#     generated_tokens = model.generate(**encoded_ar)
#     trans = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
#     return trans[0]

# def write_to_pdf(translated_lines, file_path):
#     pdf = FPDF()
#     pdf.add_page()
#     pdf.set_auto_page_break(auto=True, margin=15)
#     pdf.set_font("Arial", size=12)
    
#     for line in translated_lines:
#         pdf.multi_cell(0, 10, line)

#     pdf.output(file_path)

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/upload', methods=['POST'])
# @cross_origin(origins=["http://localhost:4200"])
# def upload_file():
#     if 'file' not in request.files:
#         return jsonify({'error': 'No file part'}), 400

#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({'error': 'No selected file'}), 400

#     temp_dir = tempfile.gettempdir()
#     file_path = os.path.join(temp_dir, file.filename)
#     os.makedirs(temp_dir, exist_ok=True)  # Ensure the temporary directory exists
#     file.save(file_path)

#     return jsonify({'message': 'File uploaded successfully', 'file_path': file_path}), 200

# @app.route('/translate', methods=['POST'])
# @cross_origin(origins=["http://localhost:4200"])
# def translate():
#     input_pdf_path = request.json.get('file_path')
#     if not input_pdf_path or not os.path.exists(input_pdf_path):
#         return jsonify({'error': 'Invalid file path'}), 400

#     def generate_translation():
#         try:
#             lines = pdf_to_text_reverse_arabic(input_pdf_path)

#             model_name = "Helsinki-NLP/opus-mt-ar-en"
#             model = MarianMTModel.from_pretrained(model_name)
#             tokenizer = MarianTokenizer.from_pretrained(model_name)

#             translated_lines = [None] * len(lines)
#             with concurrent.futures.ThreadPoolExecutor() as executor:
#                 future_to_index = {executor.submit(translate_arabic_to_english, model, tokenizer, line): idx for idx, line in enumerate(lines)}
#                 total = len(lines)
#                 for i, future in enumerate(concurrent.futures.as_completed(future_to_index)):
#                     idx = future_to_index[future]
#                     translated_lines[idx] = future.result()
#                     yield f"data: {json.dumps({'progress': (i + 1) * 100 / total})}\n\n"

#             output_pdf_path = os.path.splitext(input_pdf_path)[0] + '_translated.pdf'
#             write_to_pdf(translated_lines, output_pdf_path)
#             yield f"data: {json.dumps({'url': output_pdf_path})}\n\n"
#         except Exception as e:
#             yield f"data: {json.dumps({'error': str(e)})}\n\n"

#     return Response(stream_with_context(generate_translation()), content_type='text/event-stream')

# if __name__ == '__main__':
#     app.run(debug=True)

# import os
# from flask import Flask, request, jsonify, send_file, render_template
# from flask_cors import CORS
# import pdfplumber
# import re
# from googletrans import Translator
# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas
# from reportlab.lib.utils import ImageReader
# from io import BytesIO
# import tempfile

# app = Flask(__name__)
# CORS(app)

# def extract_text_images_from_pdf(pdf_path):
#     """Extract text and images from a PDF file."""
#     pages_content = []
#     with pdfplumber.open(pdf_path) as pdf:
#         for page in pdf.pages:
#             page_content = {
#                 "text": page.extract_text(x_tolerance=2, y_tolerance=2),
#                 "images": []
#             }
#             for image in page.images:
#                 img_bbox = (image["x0"], image["top"], image["x1"], image["bottom"])
#                 img_obj = page.within_bbox(img_bbox).to_image(resolution=300)
#                 img_data = BytesIO()
#                 img_obj.save(img_data, format='PNG')
#                 img_data.seek(0)
#                 img_bytes = img_data.read()
#                 page_content["images"].append((img_bbox, img_bytes))
#             pages_content.append(page_content)
#     return pages_content



# def arabic_to_english(text):
#     """Translate Arabic text to English using Google Translate."""
#     translator = Translator()
#     translation = translator.translate(text, src='ar', dest='en')
#     return translation.text

# def handle_line_by_line_conversion(text):
#     """Reverse lines of text to handle right-to-left Arabic."""
#     lines = text.split('\n')
#     reversed_lines = [line[::-1] for line in lines]
#     return '\n'.join(reversed_lines)

# def reverse_numbers_in_text(text):
#     """Reverse numbers in the given text."""
#     return re.sub(r'\d+', lambda x: x.group(0)[::-1], text)

# def reverse_emails_in_text(text):
#     """Reverse email addresses in the given text."""
#     email_pattern = re.compile(r'[\w\.-]+@[\w\.-]+')
#     reversed_text = email_pattern.sub(lambda x: x.group(0)[::-1], text)
#     return reversed_text
 
# def preserve_patterns_and_translate(text):
#     """Preserve patterns like 'Page X of Y' and translate the rest."""
#     # Replace '12 fo 34 egaP' with 'Page 12 of 34'
#     pattern = re.compile(r'(\d+) fo (\d+) egaP')
#     text = pattern.sub(r'Page \2 of \1', text)
   
#     # Translate the rest of the text
#     translated_text = arabic_to_english(text)
   
#     return translated_text

# def save_text_images_to_pdf(pages_content, output_pdf_path):
#     """Save the given text and images to a PDF file."""
#     c = canvas.Canvas(output_pdf_path, pagesize=letter)
#     width, height = letter
#     font_size = 10  # Fixed font size for all pages

#     for page_content in pages_content:
#         y = height - 40  # Start from top of the page

#         # Draw images first to avoid overlapping text
#         for img_bbox, img_bytes in page_content["images"]:
#             x0, top, x1, bottom = img_bbox
#             image_stream = BytesIO(img_bytes)
#             img_height = bottom - top
#             img_width = x1 - x0
#             c.drawImage(ImageReader(image_stream), x0, height - bottom, width=img_width, height=img_height)

#             # Adjust y position to avoid overlapping text with images
#             y -= img_height + 15  # Add some extra space between image and text
        
#         # Add extra space before text
#         y -= 15
        
#         # Set font size for the page
#         c.setFont("Helvetica", font_size)
        
#         # Process text
#         text_lines = page_content["text"].split('\n')
#         for line in text_lines:
#             # Split the line into words
#             words = line.split()
#             current_line = ""
#             for word in words:
#                 # Check if adding this word would exceed the available width
#                 if c.stringWidth(current_line + " " + word) > (width - 80):  # 80 is a margin value
#                     # Draw the current line
#                     c.drawString(40, y, current_line.strip())
#                     y -= 15  # Move to the next line with a fixed spacing
#                     current_line = ""
                
#                 # Add the word to the current line
#                 if current_line == "":
#                     current_line = word
#                 else:
#                     current_line += " " + word
            
#             # Draw the remaining part of the line
#             if current_line:
#                 c.drawString(40, y, current_line.strip())
#                 y -= 15  # Move to the next line with a fixed spacing

#             if y < 40:  # Create a new page if we reach the bottom of the current page
#                 c.showPage()
#                 y = height - 40

#         c.showPage()  # Create a new page for the next set of content

#     c.save()

# @app.route('/upload', methods=['POST'])
# def upload():
#     file = request.files['file']
#     if file:
#         temp_dir = tempfile.mkdtemp()
#         file_path = os.path.join(temp_dir, file.filename)
#         file.save(file_path)
#         return jsonify({'message': 'File uploaded successfully', 'file_path': file_path})
#     return jsonify({'message': 'No file uploaded'}), 400

# @app.route('/translate', methods=['POST'])
# def translate():
#     data = request.get_json()
#     file_path = data.get('file_path')
#     if file_path:
#         pages_content = extract_text_images_from_pdf(file_path)
#         for page_content in pages_content:
#             if page_content["text"]:
#                 page_content["text"] = handle_line_by_line_conversion(page_content["text"])
#                 page_content["text"] = preserve_patterns_and_translate(page_content["text"])
#                 page_content["text"] = reverse_numbers_in_text(page_content["text"])
#                 page_content["text"] = reverse_emails_in_text(page_content["text"])

#         output_pdf_path = os.path.join(tempfile.mkdtemp(), 'translated.pdf')
#         save_text_images_to_pdf(pages_content, output_pdf_path)
#         return send_file(output_pdf_path, as_attachment=False, download_name='translated.pdf')
#     return jsonify({'message': 'File path not provided'}), 400

# if __name__ == '__main__':
#     app.run(debug=True)

# import os
# from flask import Flask, request, jsonify, send_file, render_template
# from flask_cors import CORS
# import pdfplumber
# import re
# from mtranslate import translate
# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas
# from reportlab.lib.utils import ImageReader
# from io import BytesIO
# import tempfile

# app = Flask(__name__)
# CORS(app)

# def extract_text_images_from_pdf(pdf_path):
#     """Extract text and images from a PDF file."""
#     pages_content = []
#     with pdfplumber.open(pdf_path) as pdf:
#         for page in pdf.pages:
#             page_content = {
#                 "text": page.extract_text(x_tolerance=2, y_tolerance=2),
#                 "images": []
#             }
#             for image in page.images:
#                 img_bbox = (image["x0"], image["top"], image["x1"], image["bottom"])
#                 img_obj = page.within_bbox(img_bbox).to_image(resolution=300)
#                 img_data = BytesIO()
#                 img_obj.save(img_data, format='PNG')
#                 img_data.seek(0)
#                 img_bytes = img_data.read()
#                 page_content["images"].append((img_bbox, img_bytes))
#             pages_content.append(page_content)
#     return pages_content

# def arabic_to_english(text):
#     """Translate Arabic text to English using mtranslate."""
#     return translate(text, 'en', 'ar')

# def handle_line_by_line_conversion(text):
#     """Reverse lines of text to handle right-to-left Arabic."""
#     lines = text.split('\n')
#     reversed_lines = [line[::-1] for line in lines]
#     return '\n'.join(reversed_lines)

# def reverse_numbers_in_text(text):
#     """Reverse numbers in the given text."""
#     return re.sub(r'\d+', lambda x: x.group(0)[::-1], text)

# def reverse_emails_in_text(text):
#     """Reverse email addresses in the given text."""
#     email_pattern = re.compile(r'[\w\.-]+@[\w\.-]+')
#     reversed_text = email_pattern.sub(lambda x: x.group(0)[::-1], text)
#     return reversed_text

# def preserve_patterns_and_translate(text):
#     """Preserve patterns like 'Page X of Y' and translate the rest."""
#     # Replace '12 fo 34 egaP' with 'Page 12 of 34'
#     pattern = re.compile(r'(\d+) fo (\d+) egaP')
#     text = pattern.sub(r'Page \2 of \1', text)

#     # Translate the rest of the text
#     translated_text = arabic_to_english(text)
   
#     return translated_text

# def save_text_images_to_pdf(pages_content, output_pdf_path):
#     """Save the given text and images to a PDF file."""
#     c = canvas.Canvas(output_pdf_path, pagesize=letter)
#     width, height = letter
#     font_size = 10  # Fixed font size for all pages

#     for page_content in pages_content:
#         y = height - 40  # Start from top of the page

#         # Draw images first to avoid overlapping text
#         for img_bbox, img_bytes in page_content["images"]:
#             x0, top, x1, bottom = img_bbox
#             image_stream = BytesIO(img_bytes)
#             img_height = bottom - top
#             img_width = x1 - x0
#             c.drawImage(ImageReader(image_stream), x0, height - bottom, width=img_width, height=img_height)

#             # Adjust y position to avoid overlapping text with images
#             y -= img_height + 15  # Add some extra space between image and text
        
#         # Add extra space before text
#         y -= 15
        
#         # Set font size for the page
#         c.setFont("Helvetica", font_size)
        
#         # Process text
#         text_lines = page_content["text"].split('\n')
#         for line in text_lines:
#             # Split the line into words
#             words = line.split()
#             current_line = ""
#             for word in words:
#                 # Check if adding this word would exceed the available width
#                 if c.stringWidth(current_line + " " + word) > (width - 80):  # 80 is a margin value
#                     # Draw the current line
#                     c.drawString(40, y, current_line.strip())
#                     y -= 15  # Move to the next line with a fixed spacing
#                     current_line = ""
                
#                 # Add the word to the current line
#                 if current_line == "":
#                     current_line = word
#                 else:
#                     current_line += " " + word
            
#             # Draw the remaining part of the line
#             if current_line:
#                 c.drawString(40, y, current_line.strip())
#                 y -= 15  # Move to the next line with a fixed spacing

#             if y < 40:  # Create a new page if we reach the bottom of the current page
#                 c.showPage()
#                 y = height - 40

#         c.showPage()  # Create a new page for the next set of content

#     c.save()

# @app.route('/upload', methods=['POST'])
# def upload():
#     file = request.files['file']
#     if file:
#         temp_dir = tempfile.mkdtemp()
#         file_path = os.path.join(temp_dir, file.filename)
#         file.save(file_path)
#         return jsonify({'message': 'File uploaded successfully', 'file_path': file_path})
#     return jsonify({'message': 'No file uploaded'}), 400

# @app.route('/translate', methods=['POST'])
# def translate_route():
#     data = request.get_json()
#     file_path = data.get('file_path')
#     if file_path:
#         pages_content = extract_text_images_from_pdf(file_path)
#         for page_content in pages_content:
#             if page_content["text"]:
#                 page_content["text"] = handle_line_by_line_conversion(page_content["text"])
#                 page_content["text"] = preserve_patterns_and_translate(page_content["text"])
#                 page_content["text"] = reverse_numbers_in_text(page_content["text"])
#                 page_content["text"] = reverse_emails_in_text(page_content["text"])

#         output_pdf_path = os.path.join(tempfile.mkdtemp(), 'translated.pdf')
#         save_text_images_to_pdf(pages_content, output_pdf_path)
#         return send_file(output_pdf_path, as_attachment=False, download_name='translated.pdf')
#     return jsonify({'message': 'File path not provided'}), 400

# if __name__ == '__main__':
#     app.run(debug=True)

# import os
# from flask import Flask, request, jsonify, send_file
# from flask_cors import CORS
# import pdfplumber
# import re
# from transformers import MBartForConditionalGeneration, MBart50TokenizerFast
# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas
# from reportlab.lib.utils import ImageReader
# from io import BytesIO
# import tempfile

# app = Flask(__name__)
# CORS(app)

# # Load the model and tokenizer for mBART
# model_name = 'facebook/mbart-large-50-many-to-many-mmt'
# tokenizer = MBart50TokenizerFast.from_pretrained(model_name)
# model = MBartForConditionalGeneration.from_pretrained(model_name)

# def arabic_to_english(text):
#     """Translate Arabic text to English using a Hugging Face mBART model."""
#     tokenizer.src_lang = "ar_AR"
#     encoded_text = tokenizer(text, return_tensors="pt")
#     generated_tokens = model.generate(**encoded_text, forced_bos_token_id=tokenizer.lang_code_to_id["en_XX"])
#     translated_text = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
#     return translated_text[0]

# def extract_text_images_from_pdf(pdf_path):
#     """Extract text and images from a PDF file."""
#     pages_content = []
#     with pdfplumber.open(pdf_path) as pdf:
#         for page in pdf.pages:
#             page_content = {
#                 "text": page.extract_text(x_tolerance=2, y_tolerance=2),
#                 "images": []
#             }
#             for image in page.images:
#                 img_bbox = (image["x0"], image["top"], image["x1"], image["bottom"])
#                 img_obj = page.within_bbox(img_bbox).to_image(resolution=300)
#                 img_data = BytesIO()
#                 img_obj.save(img_data, format='PNG')
#                 img_data.seek(0)
#                 img_bytes = img_data.read()
#                 page_content["images"].append((img_bbox, img_bytes))
#             pages_content.append(page_content)
#     return pages_content

# def handle_line_by_line_conversion(text):
#     """Reverse lines of text to handle right-to-left Arabic."""
#     lines = text.split('\n')
#     reversed_lines = [line[::-1] for line in lines]
#     return '\n'.join(reversed_lines)

# def reverse_numbers_in_text(text):
#     """Reverse numbers in the given text."""
#     return re.sub(r'\d+', lambda x: x.group(0)[::-1], text)

# def reverse_emails_in_text(text):
#     """Reverse email addresses in the given text."""
#     email_pattern = re.compile(r'[\w\.-]+@[\w\.-]+')
#     reversed_text = email_pattern.sub(lambda x: x.group(0)[::-1], text)
#     return reversed_text

# def preserve_patterns_and_translate(text):
#     """Preserve patterns like 'Page X of Y' and translate the rest."""
#     lines = text.split('\n')
#     translated_lines = []
#     pattern = re.compile(r'(\d+) fo (\d+) egaP')
    
#     for line in lines:
#         # Replace '12 fo 34 egaP' with 'Page 12 of 34'
#         line = pattern.sub(r'Page \2 of \1', line)
#         # Translate the line
#         translated_line = arabic_to_english(line)
#         translated_lines.append(translated_line)
    
#     return '\n'.join(translated_lines)

# def save_text_images_to_pdf(pages_content, output_pdf_path):
#     """Save the given text and images to a PDF file."""
#     c = canvas.Canvas(output_pdf_path, pagesize=letter)
#     width, height = letter
#     font_size = 10  # Fixed font size for all pages

#     for page_content in pages_content:
#         y = height - 40  # Start from top of the page

#         # Draw images first to avoid overlapping text
#         for img_bbox, img_bytes in page_content["images"]:
#             x0, top, x1, bottom = img_bbox
#             image_stream = BytesIO(img_bytes)
#             img_height = bottom - top
#             img_width = x1 - x0
#             c.drawImage(ImageReader(image_stream), x0, height - bottom, width=img_width, height=img_height)

#             # Adjust y position to avoid overlapping text with images
#             y -= img_height + 15  # Add some extra space between image and text
        
#         # Add extra space before text
#         y -= 15
        
#         # Set font size for the page
#         c.setFont("Helvetica", font_size)
        
#         # Process text
#         text_lines = page_content["text"].split('\n')
#         for line in text_lines:
#             # Split the line into words
#             words = line.split()
#             current_line = ""
#             for word in words:
#                 # Check if adding this word would exceed the available width
#                 if c.stringWidth(current_line + " " + word) > (width - 80):  # 80 is a margin value
#                     # Draw the current line
#                     c.drawString(40, y, current_line.strip())
#                     y -= 15  # Move to the next line with a fixed spacing
#                     current_line = ""
                
#                 # Add the word to the current line
#                 if current_line == "":
#                     current_line = word
#                 else:
#                     current_line += " " + word
            
#             # Draw the remaining part of the line
#             if current_line:
#                 c.drawString(40, y, current_line.strip())
#                 y -= 15  # Move to the next line with a fixed spacing

#             if y < 40:  # Create a new page if we reach the bottom of the current page
#                 c.showPage()
#                 y = height - 40

#         c.showPage()  # Create a new page for the next set of content

#     c.save()

# @app.route('/upload', methods=['POST'])
# def upload():
#     file = request.files['file']
#     if file:
#         temp_dir = tempfile.mkdtemp()
#         file_path = os.path.join(temp_dir, file.filename)
#         file.save(file_path)
#         return jsonify({'message': 'File uploaded successfully', 'file_path': file_path})
#     return jsonify({'message': 'No file uploaded'}), 400

# @app.route('/translate', methods=['POST'])
# def translate():
#     data = request.get_json()
#     file_path = data.get('file_path')
#     if file_path:
#         pages_content = extract_text_images_from_pdf(file_path)
#         for page_content in pages_content:
#             if page_content["text"]:
#                 page_content["text"] = handle_line_by_line_conversion(page_content["text"])
#                 page_content["text"] = preserve_patterns_and_translate(page_content["text"])
#                 page_content["text"] = reverse_numbers_in_text(page_content["text"])
#                 page_content["text"] = reverse_emails_in_text(page_content["text"])

#         output_pdf_path = os.path.join(tempfile.mkdtemp(), 'translated.pdf')
#         save_text_images_to_pdf(pages_content, output_pdf_path)
#         return send_file(output_pdf_path, as_attachment=False, download_name='translated.pdf')
#     return jsonify({'message': 'File path not provided'}), 400

# if __name__ == '__main__':
#     app.run(debug=True)

# import os
# import threading
# from flask import Flask, request, jsonify, send_file
# from flask_cors import CORS
# import pdfplumber
# import re
# from mtranslate import translate
# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas
# from reportlab.lib.utils import ImageReader
# from io import BytesIO
# import tempfile

# app = Flask(__name__)
# CORS(app)

# translations = {}

# def extract_text_images_from_pdf(pdf_path):
#     """Extract text and images from a PDF file."""
#     pages_content = []
#     with pdfplumber.open(pdf_path) as pdf:
#         for page in pdf.pages:
#             page_content = {
#                 "text": page.extract_text(x_tolerance=2, y_tolerance=2),
#                 "images": []
#             }
#             for image in page.images:
#                 img_bbox = (image["x0"], image["top"], image["x1"], image["bottom"])
#                 img_obj = page.within_bbox(img_bbox).to_image(resolution=300)
#                 img_data = BytesIO()
#                 img_obj.save(img_data, format='PNG')
#                 img_data.seek(0)
#                 img_bytes = img_data.read()
#                 page_content["images"].append((img_bbox, img_bytes))
#             pages_content.append(page_content)
#     return pages_content

# def arabic_to_english(text):
#     """Translate Arabic text to English using mtranslate."""
#     return translate(text, 'en', 'ar')

# def handle_line_by_line_conversion(text):
#     """Reverse lines of text to handle right-to-left Arabic."""
#     lines = text.split('\n')
#     reversed_lines = [line[::-1] for line in lines]
#     return '\n'.join(reversed_lines)

# def reverse_numbers_in_text(text):
#     """Reverse numbers in the given text."""
#     return re.sub(r'\d+', lambda x: x.group(0)[::-1], text)

# def reverse_emails_in_text(text):
#     """Reverse email addresses in the given text."""
#     email_pattern = re.compile(r'[\w\.-]+@[\w\.-]+')
#     reversed_text = email_pattern.sub(lambda x: x.group(0)[::-1], text)
#     return reversed_text

# def preserve_patterns_and_translate(text):
#     """Preserve patterns like 'Page X of Y' and translate the rest."""
#     # Replace '12 fo 34 egaP' with 'Page 12 of 34'
#     pattern = re.compile(r'(\d+) fo (\d+) egaP')
#     text = pattern.sub(r'Page \2 of \1', text)

#     # Translate the rest of the text
#     translated_text = arabic_to_english(text)
   
#     return translated_text

# def save_text_images_to_pdf(pages_content, output_pdf_path):
#     """Save the given text and images to a PDF file."""
#     c = canvas.Canvas(output_pdf_path, pagesize=letter)
#     width, height = letter
#     font_size = 10  # Fixed font size for all pages

#     for page_content in pages_content:
#         y = height - 40  # Start from top of the page

#         # Draw images first to avoid overlapping text
#         for img_bbox, img_bytes in page_content["images"]:
#             x0, top, x1, bottom = img_bbox
#             image_stream = BytesIO(img_bytes)
#             img_height = bottom - top
#             img_width = x1 - x0
#             c.drawImage(ImageReader(image_stream), x0, height - bottom, width=img_width, height=img_height)

#             # Adjust y position to avoid overlapping text with images
#             y -= img_height + 15  # Add some extra space between image and text
        
#         # Add extra space before text
#         y -= 15
        
#         # Set font size for the page
#         c.setFont("Helvetica", font_size)
        
#         # Process text
#         text_lines = page_content["text"].split('\n')
#         for line in text_lines:
#             # Split the line into words
#             words = line.split()
#             current_line = ""
#             for word in words:
#                 # Check if adding this word would exceed the available width
#                 if c.stringWidth(current_line + " " + word) > (width - 80):  # 80 is a margin value
#                     # Draw the current line
#                     c.drawString(40, y, current_line.strip())
#                     y -= 15  # Move to the next line with a fixed spacing
#                     current_line = ""
                
#                 # Add the word to the current line
#                 if current_line == "":
#                     current_line = word
#                 else:
#                     current_line += " " + word
            
#             # Draw the remaining part of the line
#             if current_line:
#                 c.drawString(40, y, current_line.strip())
#                 y -= 15  # Move to the next line with a fixed spacing

#             if y < 40:  # Create a new page if we reach the bottom of the current page
#                 c.showPage()
#                 y = height - 40

#         c.showPage()  # Create a new page for the next set of content

#     c.save()

# def translate_pdf(file_path, translation_id):
#     """Perform the translation and save the translated PDF."""
#     pages_content = extract_text_images_from_pdf(file_path)
#     num_pages = len(pages_content)
    
#     for i, page_content in enumerate(pages_content):
#         if page_content["text"]:
#             page_content["text"] = handle_line_by_line_conversion(page_content["text"])
#             page_content["text"] = preserve_patterns_and_translate(page_content["text"])
#             page_content["text"] = reverse_numbers_in_text(page_content["text"])
#             page_content["text"] = reverse_emails_in_text(page_content["text"])
        
#         # Update progress
#         translations[translation_id]['progress'] = int((i + 1) / num_pages * 100)
    
#     output_pdf_path = os.path.join(tempfile.mkdtemp(), 'translated.pdf')
#     save_text_images_to_pdf(pages_content, output_pdf_path)
    
#     translations[translation_id]['status'] = 'completed'
#     translations[translation_id]['file_path'] = output_pdf_path

# @app.route('/upload', methods=['POST'])
# def upload():
#     file = request.files['file']
#     if file:
#         temp_dir = tempfile.mkdtemp()
#         file_path = os.path.join(temp_dir, file.filename)
#         file.save(file_path)
#         return jsonify({'message': 'File uploaded successfully', 'file_path': file_path})
#     return jsonify({'message': 'No file uploaded'}), 400

# @app.route('/translate', methods=['POST'])
# def translate_route():
#     data = request.get_json()
#     file_path = data.get('file_path')
#     if file_path:
#         translation_id = os.path.basename(file_path).split('.')[0]
#         translations[translation_id] = {'status': 'in_progress', 'progress': 0}
#         threading.Thread(target=translate_pdf, args=(file_path, translation_id)).start()
#         return jsonify({'message': 'Translation started', 'translation_id': translation_id})
#     return jsonify({'message': 'File path not provided'}), 400

# @app.route('/translation_status/<translation_id>', methods=['GET'])
# def translation_status(translation_id):
#     translation = translations.get(translation_id)
#     if translation:
#         return jsonify(translation)
#     return jsonify({'message': 'Translation ID not found'}), 404

# @app.route('/download/<translation_id>', methods=['GET'])
# def download(translation_id):
#     translation = translations.get(translation_id)
#     if translation and translation['status'] == 'completed':
#         return send_file(translation['file_path'], as_attachment=True, download_name='translated.pdf')
#     return jsonify({'message': 'File not available for download'}), 404

# if __name__ == '__main__':
#     app.run(debug=True)

#mtranslate table 
# import os
# import threading
# from flask import Flask, request, jsonify, send_file
# from flask_cors import CORS
# import pdfplumber
# import re
# from mtranslate import translate
# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas
# from reportlab.lib import colors
# from reportlab.platypus import Table, TableStyle
# from reportlab.lib.utils import ImageReader
# from io import BytesIO
# import tempfile

# app = Flask(__name__)
# CORS(app)

# translations = {}

# def extract_text_images_tables_from_pdf(pdf_path):
#     """Extract text, images, and tables from a PDF file."""
#     pages_content = []
#     with pdfplumber.open(pdf_path) as pdf:
#         for page in pdf.pages:
#             page_content = {
#                 "text": page.extract_text(x_tolerance=2, y_tolerance=2),
#                 "images": [],
#                 "tables": []
#             }
#             for image in page.images:
#                 img_bbox = (image["x0"], image["top"], image["x1"], image["bottom"])
#                 img_obj = page.within_bbox(img_bbox).to_image(resolution=300)
#                 img_data = BytesIO()
#                 img_obj.save(img_data, format='PNG')
#                 img_data.seek(0)
#                 img_bytes = img_data.read()
#                 page_content["images"].append((img_bbox, img_bytes))
            
#             tables = page.extract_tables()
#             page_content["tables"] = tables
            
#             pages_content.append(page_content)
#     return pages_content

# def arabic_to_english(text):
#     """Translate Arabic text to English using mtranslate."""
#     return translate(text, 'en', 'ar')

# def handle_line_by_line_conversion(text):
#     """Reverse lines of text to handle right-to-left Arabic."""
#     lines = text.split('\n')
#     reversed_lines = [line[::-1] for line in lines]
#     return '\n'.join(reversed_lines)

# def reverse_numbers_in_text(text):
#     """Reverse numbers in the given text."""
#     return re.sub(r'\d+', lambda x: x.group(0)[::-1], text)

# def reverse_emails_in_text(text):
#     """Reverse email addresses in the given text."""
#     email_pattern = re.compile(r'[\w\.-]+@[\w\.-]+')
#     reversed_text = email_pattern.sub(lambda x: x.group(0)[::-1], text)
#     return reversed_text

# def preserve_patterns_and_translate(text):
#     """Preserve patterns like 'Page X of Y' and translate the rest."""
#     # Replace '12 fo 34 egaP' with 'Page 12 of 34'
#     pattern = re.compile(r'(\d+) fo (\d+) egaP')
#     text = pattern.sub(r'Page \2 of \1', text)

#     # Translate the rest of the text
#     translated_text = arabic_to_english(text)
   
#     return translated_text

# def translate_table(table):
#     """Translate Arabic table content to English."""
#     translated_table = []
#     for row in table:
#         translated_row = [arabic_to_english(cell) if cell else '' for cell in row]
#         translated_table.append(translated_row)
#     return translated_table

# def save_text_images_tables_to_pdf(pages_content, output_pdf_path):
#     """Save the given text, images, and tables to a PDF file."""
#     c = canvas.Canvas(output_pdf_path, pagesize=letter)
#     width, height = letter
#     font_size = 10  # Fixed font size for all pages

#     for page_content in pages_content:
#         y = height - 40  # Start from top of the page

#         # Draw images first to avoid overlapping text
#         for img_bbox, img_bytes in page_content["images"]:
#             x0, top, x1, bottom = img_bbox
#             image_stream = BytesIO(img_bytes)
#             img_height = bottom - top
#             img_width = x1 - x0
#             c.drawImage(ImageReader(image_stream), x0, height - bottom, width=img_width, height=img_height)

#             # Adjust y position to avoid overlapping text with images
#             y -= img_height + 15  # Add some extra space between image and text
        
#         # Add extra space before text
#         y -= 15
        
#         # Set font size for the page
#         c.setFont("Helvetica", font_size)
        
#         # Process text
#         if page_content["text"]:
#             text_lines = page_content["text"].split('\n')
#             for line in text_lines:
#                 # Split the line into words
#                 words = line.split()
#                 current_line = ""
#                 for word in words:
#                     # Check if adding this word would exceed the available width
#                     if c.stringWidth(current_line + " " + word) > (width - 80):  # 80 is a margin value
#                         # Draw the current line
#                         c.drawString(40, y, current_line.strip())
#                         y -= 15  # Move to the next line with a fixed spacing
#                         current_line = ""
                    
#                     # Add the word to the current line
#                     if current_line == "":
#                         current_line = word
#                     else:
#                         current_line += " " + word
                
#                 # Draw the remaining part of the line
#                 if current_line:
#                     c.drawString(40, y, current_line.strip())
#                     y -= 15  # Move to the next line with a fixed spacing

#                 if y < 40:  # Create a new page if we reach the bottom of the current page
#                     c.showPage()
#                     y = height - 40
        
#         # Draw tables
#         for table in page_content["tables"]:
#             translated_table = translate_table(table)
#             table_style = TableStyle([
#                 ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
#                 ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                 ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                 ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#                 ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
#                 ('GRID', (0, 0), (-1, -1), 1, colors.black),
#             ])
#             table = Table(translated_table, style=table_style)
#             table.wrapOn(c, width, height)
#             table_height = table._height
#             table.drawOn(c, 40, y - table_height)
#             y -= table_height + 15
#             if y < 40:
#                 c.showPage()
#                 y = height - 40

#         c.showPage()  # Create a new page for the next set of content

#     c.save()

# def translate_pdf(file_path, translation_id):
#     """Perform the translation and save the translated PDF."""
#     pages_content = extract_text_images_tables_from_pdf(file_path)
#     num_pages = len(pages_content)
    
#     for i, page_content in enumerate(pages_content):
#         if page_content["text"]:
#             page_content["text"] = handle_line_by_line_conversion(page_content["text"])
#             page_content["text"] = preserve_patterns_and_translate(page_content["text"])
#             page_content["text"] = reverse_numbers_in_text(page_content["text"])
#             page_content["text"] = reverse_emails_in_text(page_content["text"])
        
#         # Update progress
#         translations[translation_id]['progress'] = int((i + 1) / num_pages * 100)
    
#     output_pdf_path = os.path.join(tempfile.mkdtemp(), 'translated.pdf')
#     save_text_images_tables_to_pdf(pages_content, output_pdf_path)
    
#     translations[translation_id]['status'] = 'completed'
#     translations[translation_id]['file_path'] = output_pdf_path

# @app.route('/upload', methods=['POST'])
# def upload():
#     file = request.files['file']
#     if file:
#         temp_dir = tempfile.mkdtemp()
#         file_path = os.path.join(temp_dir, file.filename)
#         file.save(file_path)
#         return jsonify({'message': 'File uploaded successfully', 'file_path': file_path})
#     return jsonify({'message': 'No file uploaded'}), 400

# @app.route('/translate', methods=['POST'])
# def translate_route():
#     data = request.get_json()
#     file_path = data.get('file_path')
#     if file_path:
#         translation_id = os.path.basename(file_path).split('.')[0]
#         translations[translation_id] = {'status': 'in_progress', 'progress': 0}
#         threading.Thread(target=translate_pdf, args=(file_path, translation_id)).start()
#         return jsonify({'message': 'Translation started', 'translation_id': translation_id})
#     return jsonify({'message': 'File path not provided'}), 400

# @app.route('/translation_status/<translation_id>', methods=['GET'])
# def translation_status(translation_id):
#     translation = translations.get(translation_id)
#     if translation:
#         return jsonify(translation)
#     return jsonify({'message': 'Translation ID not found'}), 404

# @app.route('/download/<translation_id>', methods=['GET'])
# def download(translation_id):
#     translation = translations.get(translation_id)
#     if translation and translation['status'] == 'completed':
#         return send_file(translation['file_path'], as_attachment=True, download_name='translated.pdf')
#     return jsonify({'message': 'File not available for download'}), 404

# if __name__ == '__main__':
#     app.run(debug=True)





# import os
# import threading
# from flask import Flask, request, jsonify, send_file
# from flask_cors import CORS
# import pdfplumber
# import arabic_reshaper
# from bidi.algorithm import get_display
# from transformers import MarianMTModel, MarianTokenizer
# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas
# from reportlab.lib import colors
# from reportlab.platypus import Table, TableStyle, Paragraph
# from reportlab.lib.styles import getSampleStyleSheet
# from reportlab.lib.utils import ImageReader
# from io import BytesIO
# import re
# import tempfile

# app = Flask(__name__)
# CORS(app)

# translations = {}

# def extract_text_images_tables_from_pdf(pdf_path):
#     """Extract text, images, and tables from a PDF file."""
#     extracted_content = []
#     with pdfplumber.open(pdf_path) as pdf:
#         for page in pdf.pages:
#             page_content = {"text": "", "translated_text": "", "images": [], "tables": []}

#             text = page.extract_text(x_tolerance=2, y_tolerance=2)
#             if text:
#                 bidi_text = get_display(arabic_reshaper.reshape(text))
#                 page_content["text"] = bidi_text

#             for image in page.images:
#                 try:
#                     img_bbox = (image["x0"], image["top"], image["x1"], image["bottom"])
#                     img_obj = page.within_bbox(img_bbox).to_image(resolution=300)
#                     img_data = BytesIO()
#                     img_obj.save(img_data, format='PNG')
#                     img_data.seek(0)
#                     img_bytes = img_data.read()
#                     page_content["images"].append((img_bbox, img_bytes))
#                 except Exception as e:
#                     print(f"Error processing image: {e}")
#                     continue

#             tables = page.extract_tables()
#             for table in tables:
#                 reshaped_table = []
#                 for row in table:
#                     reshaped_row = [get_display(arabic_reshaper.reshape(cell)) if cell else '' for cell in row]
#                     reshaped_table.append(reshaped_row)
#                 page_content["tables"].append(reshaped_table)

#             extracted_content.append(page_content)
#     return extracted_content

# def translate_arabic_to_english(model, tokenizer, lines):
#     """Translate Arabic text to English using MarianMT model."""
#     translated_lines = []
#     for line in lines:
#         translated = model.generate(**tokenizer(line, return_tensors="pt", padding=True))
#         translated_text = tokenizer.batch_decode(translated, skip_special_tokens=True)[0]
#         translated_lines.append(translated_text)
#     return translated_lines

# def clean_translation(text):
#     """Clean the translated text to remove unwanted artifacts."""
#     cleaned_text = re.sub(r'\b(?:no|not)\b', '', text, flags=re.IGNORECASE).strip()
#     return cleaned_text

# def save_text_images_tables_to_pdf(pages_content, output_pdf_path, model, tokenizer):
#     """Save the given text, images, and tables to a PDF file."""
#     c = canvas.Canvas(output_pdf_path, pagesize=letter)
#     width, height = letter
#     styles = getSampleStyleSheet()
#     styleN = styles['Normal']

#     for page_content in pages_content:
#         y = height - 40  # Start from top of the page

#         # Draw images first to avoid overlapping text
#         for img_bbox, img_bytes in page_content["images"]:
#             x0, top, x1, bottom = img_bbox
#             image_stream = BytesIO(img_bytes)
#             img_height = bottom - top
#             img_width = x1 - x0
#             c.drawImage(ImageReader(image_stream), x0, height - bottom, width=img_width, height=img_height)
#             y -= img_height + 15  # Add some extra space between image and text

#         c.setFont("Helvetica", 11)

#         translated_text = page_content["translated_text"]
#         translated_lines = translated_text.split('\n')

#         for line in translated_lines:
#             words = line.split()
#             current_line = ""
#             for word in words:
#                 if c.stringWidth(current_line + " " + word) > (width - 80):  # 80 is a margin value
#                     c.drawString(40, y, current_line.strip())
#                     y -= 15  # Move to the next line with a fixed spacing
#                     current_line = ""
#                 if current_line == "":
#                     current_line = word
#                 else:
#                     current_line += " " + word
#             if current_line:
#                 c.drawString(40, y, current_line.strip())
#                 y -= 15  # Move to the next line with a fixed spacing

#             if y < 40:  # Create a new page if we reach the bottom of the current page
#                 c.showPage()
#                 y = height - 40

#         # Draw tables
#         for table in page_content["tables"]:
#             table_style = TableStyle([
#                 ('BACKGROUND', (0, 0), (-1, -1), colors.white),
#                 ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
#                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                 ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
#                 ('FONTSIZE', (0, 0), (-1, -1), 10),
#                 ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
#                 ('TOPPADDING', (0, 0), (-1, -1), 12),
#                 ('GRID', (0, 0), (-1, -1), 1, colors.black),
#                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                 ('WORDWRAP', (0, 0), (-1, -1), 'CJK')
#             ])

#             wrapped_table = []
#             for row in table:
#                 wrapped_row = [Paragraph(cell, styleN) for cell in row]
#                 wrapped_table.append(wrapped_row)

#             col_widths = [(width - 80) / len(wrapped_table[0])] * len(wrapped_table[0])  # Adjust column width to fit page
#             t = Table(wrapped_table, colWidths=col_widths)
#             t.setStyle(table_style)
#             w, h = t.wrap(width, y)
#             if h > y:
#                 c.showPage()
#                 y = height - 40
#             t.drawOn(c, 40, y - h)
#             y -= h + 15

#         c.showPage()  # Create a new page for the next set of content

#     c.save()

# def translate_pdf(file_path, translation_id):
#     """Perform the translation and save the translated PDF."""
#     extracted_content = extract_text_images_tables_from_pdf(file_path)

#     model_name = "Helsinki-NLP/opus-mt-ar-en"
#     model = MarianMTModel.from_pretrained(model_name)
#     tokenizer = MarianTokenizer.from_pretrained(model_name)

#     for page_content in extracted_content:
#         arabic_text = page_content["text"]
#         translated_lines = translate_arabic_to_english(model, tokenizer, arabic_text.split('\n'))
#         cleaned_translated_lines = [clean_translation(line) for line in translated_lines]
#         page_content["translated_text"] = '\n'.join(cleaned_translated_lines)

#         # Translate tables
#         translated_tables = []
#         for table in page_content["tables"]:
#             translated_table = []
#             for row in table:
#                 translated_row = translate_arabic_to_english(model, tokenizer, row)
#                 cleaned_translated_row = [clean_translation(cell) for cell in translated_row]
#                 translated_table.append(cleaned_translated_row)
#             translated_tables.append(translated_table)
#         page_content["tables"] = translated_tables

#         translations[translation_id]['progress'] += 1 / len(extracted_content) * 100

#     output_pdf_path = os.path.join(tempfile.mkdtemp(), 'translated.pdf')
#     save_text_images_tables_to_pdf(extracted_content, output_pdf_path, model, tokenizer)

#     translations[translation_id]['status'] = 'completed'
#     translations[translation_id]['file_path'] = output_pdf_path

# @app.route('/upload', methods=['POST'])
# def upload():
#     file = request.files['file']
#     if file:
#         temp_dir = tempfile.mkdtemp()
#         file_path = os.path.join(temp_dir, file.filename)
#         file.save(file_path)
#         return jsonify({'message': 'File uploaded successfully', 'file_path': file_path})
#     return jsonify({'message': 'No file uploaded'}), 400

# @app.route('/translate', methods=['POST'])
# def translate_route():
#     data = request.get_json()
#     file_path = data.get('file_path')
#     if file_path:
#         translation_id = os.path.basename(file_path).split('.')[0]
#         translations[translation_id] = {'status': 'in_progress', 'progress': 0}
#         threading.Thread(target=translate_pdf, args=(file_path, translation_id)).start()
#         return jsonify({'message': 'Translation started', 'translation_id': translation_id})
#     return jsonify({'message': 'File path not provided'}), 400

# @app.route('/translation_status/<translation_id>', methods=['GET'])
# def translation_status(translation_id):
#     translation = translations.get(translation_id)
#     if translation:
#         return jsonify(translation)
#     return jsonify({'message': 'Translation ID not found'}), 404

# @app.route('/download/<translation_id>', methods=['GET'])
# def download(translation_id):
#     translation = translations.get(translation_id)
#     if translation and translation['status'] == 'completed':
#         return send_file(translation['file_path'], as_attachment=True)
#     return jsonify({'message': 'File not found or translation not completed'}), 404

# if __name__ == '__main__':
#     app.run(debug=True)



# import os
# import threading
# from flask import Flask, request, jsonify, send_file
# from flask_cors import CORS
# import pdfplumber
# import arabic_reshaper
# from bidi.algorithm import get_display
# from transformers import MarianMTModel, MarianTokenizer
# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas
# from reportlab.lib import colors
# from reportlab.platypus import Table, TableStyle, Paragraph
# from reportlab.lib.styles import getSampleStyleSheet
# from reportlab.lib.utils import ImageReader
# from io import BytesIO
# import re
# import tempfile
# from docx import Document
# from docx.shared import Pt
# from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
# from docx2pdf import convert as docx2pdf_convert
# from pdf2docx import Converter
# import pythoncom
# from datetime import datetime


# app = Flask(__name__)
# CORS(app)

# translations = {
#      1: {'status': 'completed', 'initial_format': 'pdf'},
#      2: {'status': 'completed', 'initial_format': 'docx'},
# }

# def extract_text_images_tables_from_pdf(pdf_path):
#     """Extract text, images, and tables from a PDF file."""
#     extracted_content = []
#     with pdfplumber.open(pdf_path) as pdf:
#         for page in pdf.pages:
#             page_content = {"text": "", "translated_text": "", "images": [], "tables": []}

#             text = page.extract_text(x_tolerance=2, y_tolerance=2)
#             if text:
#                 bidi_text = get_display(arabic_reshaper.reshape(text))
#                 page_content["text"] = bidi_text

#             for image in page.images:
#                 try:
#                     img_bbox = (image["x0"], image["top"], image["x1"], image["bottom"])
#                     img_obj = page.within_bbox(img_bbox).to_image(resolution=300)
#                     img_data = BytesIO()
#                     img_obj.save(img_data, format='PNG')
#                     img_data.seek(0)
#                     img_bytes = img_data.read()
#                     page_content["images"].append((img_bbox, img_bytes))
#                 except Exception as e:
#                     print(f"Error processing image: {e}")
#                     continue

#             tables = page.extract_tables()
#             for table in tables:
#                 reshaped_table = []
#                 for row in table:
#                     reshaped_row = [get_display(arabic_reshaper.reshape(cell)) if cell else '' for cell in row]
#                     reshaped_table.append(reshaped_row)
#                 page_content["tables"].append(reshaped_table)

#             extracted_content.append(page_content)
#     return extracted_content

# def translate_arabic_to_english(model, tokenizer, lines):
#     """Translate Arabic text to English using MarianMT model."""
#     translated_lines = []
#     for line in lines:
#         translated = model.generate(**tokenizer(line, return_tensors="pt", padding=True))
#         translated_text = tokenizer.batch_decode(translated, skip_special_tokens=True)[0]
#         translated_lines.append(translated_text)
#     return translated_lines

# def clean_translation(text):
#     """Clean the translated text to remove unwanted artifacts."""
#     text = text.replace("Ta &apos; air", "Name")
#     text = text.replace("Emil", "Email")
#     text = text.replace("date", "Date")
#     text = text.replace("Page 1 of 2", "")
#     text = text.replace("Page 2 of 2", "")
#     text = text.replace("Page 2 of 2", "").replace("land,","").replace("&apos; s", "").replace("hey,","").replace("Hey,","").replace("H-E-E-E-E-E-E-E-E","").replace("Arr-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L","").replace("land,","").replace("Argh!","").replace("Oh, my God.","775").replace("&gt","").replace("oh,","").replace("%20","20%").replace("...","").replace("L-L-L-L-L-L-L-L","").replace(",,,","")
#     text = text.replace("&apos;","").replace("-------L-L-L-L-L","").replace("Temporarily hysterical","Food allowance").replace("Screw it","Medical allowance").replace("oh.","").replace(", , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , ,","push four")
#     text = text.replace("Y-","").replace("R","").replace("Y","")
#     text = text.replace("LA","Date")
    
#     cleaned_text = re.sub(r'\b(?:no|not|non-|, ,)\b', '', text, flags=re.IGNORECASE).strip()
#     return cleaned_text

# def save_text_images_tables_to_pdf(pages_content, output_pdf_path, model, tokenizer):
#     """Save the given text, images, and tables to a PDF file."""
#     c = canvas.Canvas(output_pdf_path, pagesize=letter)
#     width, height = letter
#     styles = getSampleStyleSheet()
#     styleN = styles['Normal']

#     for page_content in pages_content:
#         y = height - 40  # Start from top of the page

#         # Draw images first to avoid overlapping text
#         for img_bbox, img_bytes in page_content["images"]:
#             x0, top, x1, bottom = img_bbox
#             image_stream = BytesIO(img_bytes)
#             img_height = bottom - top
#             img_width = x1 - x0
#             c.drawImage(ImageReader(image_stream), x0, height - bottom, width=img_width, height=img_height)
#             y -= img_height + 15  # Add some extra space between image and text

#         c.setFont("Helvetica", 11)

#         translated_text = page_content["translated_text"]
#         translated_lines = translated_text.split('\n')

#         for line in translated_lines:
#             words = line.split()
#             current_line = ""
#             for word in words:
#                 if c.stringWidth(current_line + " " + word) > (width - 80):  # 80 is a margin value
#                     c.drawString(40, y, current_line.strip())
#                     y -= 15  # Move to the next line with a fixed spacing
#                     current_line = ""
#                 if current_line == "":
#                     current_line = word
#                 else:
#                     current_line += " " + word
#             if current_line:
#                 c.drawString(40, y, current_line.strip())
#                 y -= 15  # Move to the next line with a fixed spacing

#             if y < 40:  # Create a new page if we reach the bottom of the current page
#                 c.showPage()
#                 y = height - 40

#         # Draw tables
#         for table in page_content["tables"]:
#             table_style = TableStyle([
#                 ('BACKGROUND', (0, 0), (-1, -1), colors.white),
#                 ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
#                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                 ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
#                 ('FONTSIZE', (0, 0), (-1, -1), 10),
#                 ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
#                 ('TOPPADDING', (0, 0), (-1, -1), 12),
#                 ('GRID', (0, 0), (-1, -1), 1, colors.black),
#                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                 ('WORDWRAP', (0, 0), (-1, -1), 'CJK')
#             ])

#             wrapped_table = []
#             for row in table:
#                 wrapped_row = [Paragraph(cell, styleN) for cell in row]
#                 wrapped_table.append(wrapped_row)

#             col_widths = [(width - 80) / len(wrapped_table[0])] * len(wrapped_table[0])  # Adjust column width to fit page
#             t = Table(wrapped_table, colWidths=col_widths)
#             t.setStyle(table_style)
#             w, h = t.wrap(width, y)
#             if h > y:
#                 c.showPage()
#                 y = height - 40
#             t.drawOn(c, 40, y - h)
#             y -= h + 15

#         c.showPage()  # Create a new page for the next set of content

#     c.save()

# def save_text_images_tables_to_docx(pages_content, output_docx_path):
#     """Save the given text, images, and tables to a DOCX file."""
#     doc = Document()

#     for page_content in pages_content:
#         translated_text = page_content["translated_text"]
#         translated_lines = translated_text.split('\n')

#         for line in translated_lines:
#             p = doc.add_paragraph(line)
#             p.paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT

#         for table in page_content["tables"]:
#             t = doc.add_table(rows=len(table), cols=len(table[0]))
#             t.style = 'Table Grid'
#             for row_idx, row in enumerate(table):
#                 for col_idx, cell_text in enumerate(row):
#                     cell = t.cell(row_idx, col_idx)
#                     cell.text = cell_text

#     doc.save(output_docx_path)

# def translate_pdf(file_path, translation_id, initial_format):
#     """Perform the translation and save the translated PDF file."""
#     extracted_content = extract_text_images_tables_from_pdf(file_path)
    
#     model_name = "Helsinki-NLP/opus-mt-ar-en"
#     tokenizer = MarianTokenizer.from_pretrained(model_name)
#     model = MarianMTModel.from_pretrained(model_name)

#     for page_content in extracted_content:
#         # Translate text content
#         lines = page_content["text"].split('\n')
#         translated_lines = translate_arabic_to_english(model, tokenizer, lines)
#         cleaned_lines = [clean_translation(line) for line in translated_lines]
#         page_content["translated_text"] = "\n".join(cleaned_lines)
        
#         # Translate table contents
#         translated_tables = []
#         for table in page_content["tables"]:
#             translated_table = []
#             for row in table:
#                 translated_row = translate_arabic_to_english(model, tokenizer, row)
#                 cleaned_row = [clean_translation(cell) for cell in translated_row]
#                 translated_table.append(cleaned_row)
#             translated_tables.append(translated_table)
#         page_content["tables"] = translated_tables

#     output_dir = tempfile.mkdtemp()
#     output_pdf_path = os.path.join(output_dir, "translated_output.pdf")
#     save_text_images_tables_to_pdf(extracted_content, output_pdf_path, model, tokenizer)
#     translations[translation_id] = {"status": "completed", "file_path": output_pdf_path, "initial_format": initial_format}

# def convert_docx_to_pdf(docx_path):
#     """Convert DOCX to PDF using the docx2pdf library."""
#     output_pdf_path = docx_path.replace('.docx', '.pdf')
#     docx2pdf_convert(docx_path, output_pdf_path)
#     return output_pdf_path

# def convert_pdf_to_docx(pdf_path):
#     """Convert PDF to DOCX using the pdf2docx library."""
#     output_docx_path = pdf_path.replace('.pdf', '.docx')
#     cv = Converter(pdf_path)
#     cv.convert(output_docx_path, start=0, end=None)
#     cv.close()
#     return output_docx_path

# @app.route('/upload', methods=['POST'])
# def upload():
#     pythoncom.CoInitialize()
#     """Handle file upload and initiate the translation process."""
#     file = request.files['file']
#     if file:
#         temp_dir = tempfile.mkdtemp()
#         file_path = os.path.join(temp_dir, file.filename)
#         file.save(file_path)

#         initial_format = 'pdf' if file.filename.endswith('.pdf') else 'docx'
        
#         if initial_format == 'docx':
#             file_path = convert_docx_to_pdf(file_path)

#         return jsonify({'message': 'File uploaded successfully', 'file_path': file_path, 'initial_format': initial_format})
#     return jsonify({'message': 'No file uploaded'}), 400

# @app.route('/translate', methods=['POST'])
# def translate():
#     """Start the translation process."""
#     data = request.get_json()
#     file_path = data.get('file_path')
#     initial_format = data.get('initial_format')

#     if file_path:
#         translation_id = str(len(translations) + 1)
#         translations[translation_id] = {"status": "in_progress", "file_path": None}

#         translation_thread = threading.Thread(target=translate_pdf, args=(file_path, translation_id, initial_format))
#         translation_thread.start()

#         return jsonify({'message': 'Translation started', 'translation_id': translation_id})
#     return jsonify({'message': 'File path not provided'}), 400

# @app.route('/translation_status/<translation_id>', methods=['GET'])
# def translation_status(translation_id):
#     """Check the status of the translation."""
#     translation = translations.get(translation_id)
#     if translation:
#         return jsonify({'status': translation['status'], 'file_path': translation['file_path']})
#     return jsonify({'status': 'not_found'}), 404

# @app.route('/download/<translation_id>', methods=['GET'])
# def download_translated(translation_id):
#     """Download the translated document in the initial format."""
#     translation = translations.get(translation_id)
#     if translation and translation['status'] == 'completed':
#         file_path = translation['file_path']
#         initial_format = translation.get('initial_format')

#         if initial_format == 'docx' and file_path.endswith('.pdf'):
#             file_path = convert_pdf_to_docx(file_path)
#         elif initial_format == 'pdf' and file_path.endswith('.docx'):
#             file_path = convert_docx_to_pdf(file_path)
            
#         return send_file(file_path, as_attachment=True)
#     return jsonify({'message': 'File not found or translation not completed'}), 404

# @app.route('/preview/<translation_id>', methods=['GET'])
# def download_pdf(translation_id):
#     """Download the translated PDF file."""
#     translation = translations.get(translation_id)
#     if translation and translation['status'] == 'completed':
#         file_path = translation['file_path']
#         return send_file(file_path, as_attachment=False)
#     return jsonify({'message': 'File not found or translation not completed'}), 404

# @app.route('/fetch_translated_files', methods=['GET'])
# def fetch_translated_files():
#     files = []
#     for translation_id, translation in translations.items():
#         if translation['status'] == 'completed':
#             current_datetime = datetime.now()  # Define current_datetime here
#             files.append({
#                 'fileName': f"translated_{translation_id}.{translation.get('initial_format', 'pdf')}",
#                 'downloadLink': f"http://localhost:5001/download/{translation_id}",
#                 'userName': 'Fahad',  # Assuming the user name is Fahad
#                 'liveDate': current_datetime.strftime('%Y-%m-%d'),
#                 'liveTime': current_datetime.strftime('%H:%M:%S')
#             })
#     return jsonify(files)
  
import os
import threading
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pdfplumber
import arabic_reshaper
from bidi.algorithm import get_display
from transformers import MarianMTModel, MarianTokenizer
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.utils import ImageReader
from io import BytesIO
import re
import tempfile
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx2pdf import convert as docx2pdf_convert
from pdf2docx import Converter
import pythoncom
from datetime import datetime
import json
import random
import string
 
app = Flask(__name__)
CORS(app)
 
translations = {
    "1": {
        "file_name": "example.pdf",
        "translation_date": "2024-08-02",
        "translation_time": "12:00:00"
    },
    "2": {
        "file_name": "another_example.pdf",
        "translation_date": "2024-08-02",
        "translation_time": "12:30:00"
    }
}
 
def generate_random_username():
    """Generate a random username."""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
 
def extract_text_images_tables_from_pdf(pdf_path):
    """Extract text, images, and tables from a PDF file."""
    extracted_content = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_content = {"text": "", "translated_text": "", "images": [], "tables": []}
 
            text = page.extract_text(x_tolerance=2, y_tolerance=2)
            if text:
                bidi_text = get_display(arabic_reshaper.reshape(text))
                page_content["text"] = bidi_text
 
            for image in page.images:
                try:
                    img_bbox = (image["x0"], image["top"], image["x1"], image["bottom"])
                    img_obj = page.within_bbox(img_bbox).to_image(resolution=300)
                    img_data = BytesIO()
                    img_obj.save(img_data, format='PNG')
                    img_data.seek(0)
                    img_bytes = img_data.read()
                    page_content["images"].append((img_bbox, img_bytes))
                except Exception as e:
                    print(f"Error processing image: {e}")
                    continue
 
            tables = page.extract_tables()
            for table in tables:
                reshaped_table = []
                for row in table:
                    reshaped_row = [get_display(arabic_reshaper.reshape(cell)) if cell else '' for cell in row]
                    reshaped_table.append(reshaped_row)
                page_content["tables"].append(reshaped_table)
 
            extracted_content.append(page_content)
    return extracted_content
 
def translate_arabic_to_english(model, tokenizer, lines):
    """Translate Arabic text to English using MarianMT model."""
    translated_lines = []
    for line in lines:
        translated = model.generate(**tokenizer(line, return_tensors="pt", padding=True))
        translated_text = tokenizer.batch_decode(translated, skip_special_tokens=True)[0]
        translated_lines.append(translated_text)
    return translated_lines
 
def clean_translation(text):
    """Clean the translated text to remove unwanted artifacts."""
    text = text.replace("Ta &apos; air", "Name")
    text = text.replace("Emil", "Email")
    text = text.replace("date", "Date")
    text = text.replace("Page 1 of 2", "")
    text = text.replace("Page 2 of 2", "")
    text = text.replace("Page 2 of 2", "").replace("land,","").replace("&apos; s", "").replace("hey,","").replace("Hey,","").replace("H-E-E-E-E-E-E-E-E","").replace("Arr-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L-L","").replace("land,","").replace("Argh!","").replace("Oh, my God.","775").replace("&gt","").replace("oh,","").replace("%20","20%").replace("...","").replace("L-L-L-L-L-L-L-L","").replace(",,,","")
    text = text.replace("&apos;","").replace("-------L-L-L-L-L","").replace("Temporarily hysterical","Food allowance").replace("Screw it","Medical allowance").replace("oh.","").replace(", , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , , ,","push four")
    text = text.replace("Y-","").replace("R","").replace("Y","")
    text = text.replace("LA","Date")
   
    cleaned_text = re.sub(r'\b(?:no|not|non-|, ,)\b', '', text, flags=re.IGNORECASE).strip()
    return cleaned_text
 
def save_text_images_tables_to_pdf(pages_content, output_pdf_path, model, tokenizer):
    """Save the given text, images, and tables to a PDF file."""
    c = canvas.Canvas(output_pdf_path, pagesize=letter)
    width, height = letter
    styles = getSampleStyleSheet()
    styleN = styles['Normal']
 
    for page_content in pages_content:
        y = height - 40  # Start from top of the page
 
        # Draw images first to avoid overlapping text
        for img_bbox, img_bytes in page_content["images"]:
            x0, top, x1, bottom = img_bbox
            image_stream = BytesIO(img_bytes)
            img_height = bottom - top
            img_width = x1 - x0
            c.drawImage(ImageReader(image_stream), x0, height - bottom, width=img_width, height=img_height)
            y -= img_height + 15  # Add some extra space between image and text
 
        c.setFont("Helvetica", 11)
 
        translated_text = page_content["translated_text"]
        translated_lines = translated_text.split('\n')
 
        for line in translated_lines:
            words = line.split()
            current_line = ""
            for word in words:
                if c.stringWidth(current_line + " " + word) > (width - 80):  # 80 is a margin value
                    c.drawString(40, y, current_line.strip())
                    y -= 15  # Move to the next line with a fixed spacing
                    current_line = ""
                if current_line == "":
                    current_line = word
                else:
                    current_line += " " + word
            if current_line:
                c.drawString(40, y, current_line.strip())
                y -= 15  # Move to the next line with a fixed spacing
 
            if y < 40:  # Create a new page if we reach the bottom of the current page
                c.showPage()
                y = height - 40
 
        # Draw tables
        for table in page_content["tables"]:
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('WORDWRAP', (0, 0), (-1, -1), 'CJK')
            ])
 
            wrapped_table = []
            for row in table:
                wrapped_row = [Paragraph(cell, styleN) for cell in row]
                wrapped_table.append(wrapped_row)
 
            col_widths = [(width - 80) / len(wrapped_table[0])] * len(wrapped_table[0])  # Adjust column width to fit page
            t = Table(wrapped_table, colWidths=col_widths)
            t.setStyle(table_style)
            w, h = t.wrap(width, y)
            if h > y:
                c.showPage()
                y = height - 40
            t.drawOn(c, 40, y - h)
            y -= h + 15
 
        c.showPage()  # Create a new page for the next set of content
 
    c.save()
 
def save_text_images_tables_to_docx(pages_content, output_docx_path):
    """Save the given text, images, and tables to a DOCX file."""
    doc = Document()
 
    for page_content in pages_content:
        translated_text = page_content["translated_text"]
        translated_lines = translated_text.split('\n')
 
        for line in translated_lines:
            p = doc.add_paragraph(line)
            p.paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
 
        for table in page_content["tables"]:
            t = doc.add_table(rows=len(table), cols=len(table[0]))
            t.style = 'Table Grid'
            for row_idx, row in enumerate(table):
                for col_idx, cell_text in enumerate(row):
                    cell = t.cell(row_idx, col_idx)
                    cell.text = cell_text
 
    doc.save(output_docx_path)
 
 
 
def translate_pdf(file_path, translation_id, initial_format):
    extracted_content = extract_text_images_tables_from_pdf(file_path)
    model_name = "Helsinki-NLP/opus-mt-ar-en"
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)
 
    for page_content in extracted_content:
        lines = page_content["text"].split('\n')
        translated_lines = translate_arabic_to_english(model, tokenizer, lines)
        cleaned_lines = [clean_translation(line) for line in translated_lines]
        page_content["translated_text"] = "\n".join(cleaned_lines)
 
        translated_tables = []
        for table in page_content["tables"]:
            translated_table = []
            for row in table:
                translated_row = translate_arabic_to_english(model, tokenizer, row)
                cleaned_row = [clean_translation(cell) for cell in translated_row]
                translated_table.append(cleaned_row)
            translated_tables.append(translated_table)
        page_content["tables"] = translated_tables
 
    output_dir = tempfile.mkdtemp()
    output_pdf_path = os.path.join(output_dir, "translated_output.pdf")
    save_text_images_tables_to_pdf(extracted_content, output_pdf_path, model, tokenizer)
 
    translation_details = {
        "status": "completed",
        "file_path": output_pdf_path,
        "download_link": output_pdf_path,
        "initial_format": initial_format,
        "file_name": os.path.basename(file_path),
        "translation_time": datetime.now().strftime("%H:%M:%S"),
        "translation_date": datetime.now().strftime("%Y-%m-%d")
    }
    translations[translation_id] = translation_details
    save_translations(translations)
 
 
 
 
def convert_docx_to_pdf(docx_path):
    """Convert DOCX to PDF using the docx2pdf library."""
    output_pdf_path = docx_path.replace('.docx', '.pdf')
    docx2pdf_convert(docx_path, output_pdf_path)
    return output_pdf_path
 
def convert_pdf_to_docx(pdf_path):
    """Convert PDF to DOCX using the pdf2docx library."""
    output_docx_path = pdf_path.replace('.pdf', '.docx')
    cv = Converter(pdf_path)
    cv.convert(output_docx_path, start=0, end=None)
    cv.close()
    return output_docx_path
 
@app.route('/upload', methods=['POST'])
def upload():
    pythoncom.CoInitialize()
    """Handle file upload and initiate the translation process."""
    file = request.files['file']
    if file:
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, file.filename)
        file.save(file_path)
 
        initial_format = 'pdf' if file.filename.endswith('.pdf') else 'docx'
       
        if initial_format == 'docx':
            file_path = convert_docx_to_pdf(file_path)
 
        return jsonify({'message': 'File uploaded successfully', 'file_path': file_path, 'initial_format': initial_format})
    return jsonify({'message': 'No file uploaded'}), 400
 
@app.route('/translate', methods=['POST'])
def translate():
    """Start the translation process."""
    data = request.get_json()
    file_path = data.get('file_path')
    initial_format = data.get('initial_format')
 
    if file_path:
        translation_id = str(len(translations) + 1)
        translations[translation_id] = {"status": "in_progress", "file_path": None}
 
        translation_thread = threading.Thread(target=translate_pdf, args=(file_path, translation_id, initial_format))
        translation_thread.start()
 
        return jsonify({'message': 'Translation started', 'translation_id': translation_id})
    return jsonify({'message': 'File path not provided'}), 400
 
@app.route('/translation_status/<translation_id>', methods=['GET'])
def translation_status(translation_id):
    """Check the status of the translation."""
    translation = translations.get(translation_id)
    if translation:
        return jsonify({'status': translation['status'], 'file_path': translation['file_path']})
    return jsonify({'status': 'not_found'}), 404
 
@app.route('/download/<translation_id>', methods=['GET'])
def download_translated(translation_id):
    """Download the translated document in the initial format."""
    translation = translations.get(translation_id)
    if translation and translation['status'] == 'completed':
        file_path = translation['file_path']
        initial_format = translation.get('initial_format')
 
        if initial_format == 'docx' and file_path.endswith('.pdf'):
            file_path = convert_pdf_to_docx(file_path)
        elif initial_format == 'pdf' and file_path.endswith('.docx'):
            file_path = convert_docx_to_pdf(file_path)
           
        return send_file(file_path, as_attachment=True)
    return jsonify({'message': 'File not found or translation not completed'}), 404
 
@app.route('/preview/<translation_id>', methods=['GET'])
def download_pdf(translation_id):
    """Download the translated PDF file."""
    translation = translations.get(translation_id)
    if translation and translation['status'] == 'completed':
        file_path = translation['file_path']
        return send_file(file_path, as_attachment=False)
    return jsonify({'message': 'File not found or translation not completed'}), 404
 
@app.route('/translations', methods=['GET'])
def get_translations():
    """Get the list of translations."""
    return jsonify(list(translations.values()))
 
TRANSLATIONS_FILE = 'translations.json'
 
def load_translations():
    """Load translations from the JSON file."""
    if os.path.exists(TRANSLATIONS_FILE):
        with open(TRANSLATIONS_FILE, 'r') as file:
            return json.load(file)
    return {}
 
def save_translations(translations):
    """Save translations to the JSON file."""
    with open(TRANSLATIONS_FILE, 'w') as file:
        json.dump(translations, file)
 
@app.route('/download/<translation_id>', methods=['GET'])
def download_file(translation_id):
    translation = translations.get(translation_id)
    if translation and 'file_path' in translation:
        file_path = translation['file_path']
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
    return jsonify({"message": "File not found or translation not completed"}), 404
 
translations = load_translations()
 
 
if __name__ == '__main__':
    app.run(debug=False, use_reloader=False, port=5001)