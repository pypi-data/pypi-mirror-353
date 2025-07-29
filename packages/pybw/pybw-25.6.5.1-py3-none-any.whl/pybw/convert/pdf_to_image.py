# -*- coding: utf-8 -*-
"""
author: Bowei Pu at 2024.11.01
version: 2024.11.01

Extract pdf file to image files
"""

import os
from tqdm import tqdm
import fitz  # PyMuPDF



def extract_images_from_pdf(file, dire_out):
    # 打开 PDF 文件
    pdf_document = fitz.open(file)
    
    # 检查输出文件夹是否存在，如果不存在则创建
    if not os.path.exists(dire_out):
        os.makedirs(dire_out)

    image_count = 0

    # 遍历每一页
    for page_number in tqdm(range(len(pdf_document))):
        page = pdf_document[page_number]
        image_list = page.get_images(full=True)

        # 遍历每一页的所有图片
        for img_index, img in enumerate(image_list):
            xref = img[0]  # 图片的引用
            base_image = pdf_document.extract_image(xref)  # 提取图片
            image_bytes = base_image['image']  # 获取图片的字节数据
            image_ext = base_image['ext']  # 获取图片的扩展名

            # 生成输出文件名，包含页面编号
            image_count += 1
            image_filename = os.path.join(dire_out, 
                f"img_{page_number + 1:03d}_{img_index + 1:03d}.{image_ext}")

            # 将图片保存到指定文件夹
            with open(image_filename, "wb") as image_file:
                image_file.write(image_bytes)

    print(f"Extracted {image_count} images to dir '{dire_out}'.\n")



if __name__ == '__main__':
    a = 1

    
    