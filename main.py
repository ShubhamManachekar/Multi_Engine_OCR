import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image
import concurrent.futures
import shutil

from src.image_azure_caption import process_image_caption
from src.ocr_utils import extract_images_from_docx, process_image_tesseract, process_image_easyocr, extract_text_from_docx, process_pdf, process_images_with_caption, generate_unique_name

def write_image_captions_to_file(image_captions, file_path):
    with open(file_path, "a", encoding="utf-8") as txt_file:
        txt_file.write("\n\nImage Captions:\n")
        txt_file.write("\n".join(image_captions))

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(title="Select Input File")

    if not file_path:
        print("No file selected. Exiting...")
    else:
        unique_name = generate_unique_name(file_path)  # Define unique_name here
        output_folder = "output_files"
        os.makedirs(output_folder, exist_ok=True)
        combined_output_folder = "combined_output"
        os.makedirs(combined_output_folder, exist_ok=True)

        extracted_text = ""
        extracted_images = []
        image_captions = []  # List to store image captions

        if file_path.lower().endswith('.docx'):
            image_dir = extract_images_from_docx(file_path)
            extracted_text = extract_text_from_docx(file_path)

            if extracted_text:
                text_filename = f"extracted_text_{unique_name}.txt"
                with open(os.path.join(output_folder, text_filename), "w", encoding="utf-8") as txt_file:
                    txt_file.write(extracted_text)
                print(f"Extraction completed. Text saved as: {text_filename}")

            if image_dir:
                image_captions = process_images_with_caption(image_dir)
                print("Image captioning completed.")
                # Write image captions to the combined output file
                combined_output = extracted_text + "\n"
                combined_text_filename = f"combined_text_{unique_name}.txt"
                write_image_captions_to_file(image_captions, os.path.join(combined_output_folder, combined_text_filename))
                print(f"Combined output with image captions saved as: {combined_text_filename}")

            if image_dir and os.path.exists(image_dir):
                shutil.rmtree(image_dir)  # Delete the temporary image directory

        elif file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff')):
            image = Image.open(file_path)
            extracted_text = process_image_tesseract(image) + process_image_easyocr(image)
            if extracted_text:
                text_filename = f"extracted_text_{unique_name}.txt"
                with open(os.path.join(output_folder, text_filename), "w", encoding="utf-8") as txt_file:
                    txt_file.write(extracted_text)
                print(f"Extraction completed. Text saved as: {text_filename}")

            # Image captioning for the selected image
            image_caption = process_image_caption(file_path)
            print("Image caption:", image_caption)
            # Write image caption to the combined output file
            combined_output = extracted_text + "\n\nImage Caption:\n" + image_caption
            combined_text_filename = f"combined_text_{unique_name}.txt"
            with open(os.path.join(combined_output_folder, combined_text_filename), "w", encoding="utf-8") as txt_file:
                txt_file.write(combined_output)
            print(f"Combined output with image caption saved as: {combined_text_filename}")

        elif file_path.lower().endswith('.pdf'):
            try:
                poppler_path = r"C:\Program Files\poppler-23.11.0\Library\bin"
                extracted_text = process_pdf(file_path, poppler_path, output_folder)
                if extracted_text:
                    text_filename = f"extracted_text_{unique_name}.txt"
                    with open(os.path.join(output_folder, text_filename), "w", encoding="utf-8") as txt_file:
                        txt_file.write(extracted_text)
                    print(f"Extraction completed. Text saved as: {text_filename}")
            except Exception as e:
                print(f"An error occurred during PDF processing: {e}")
        else:
            print(f"Unsupported file format: {file_path}")

        # If extracted text is empty, save image captions to a separate file
        if not extracted_text and image_captions:
            img_caption_filename = f"img_caption_{unique_name}.txt"
            with open(os.path.join(output_folder, img_caption_filename), "w", encoding="utf-8") as txt_file:
                txt_file.write("\n".join(image_captions))
            print(f"Image captions saved as: {img_caption_filename}")
