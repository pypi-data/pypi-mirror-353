from setuptools import setup, find_packages

# Read long description from README.md
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "2print (also known as toprint) - A comprehensive printing solution for HTML, PDF, ZPL, and image formats with printer support. Perfect for converting and printing documents in various formats including HTML to PDF, PDF to print, ZPL label printing, and image processing."

setup(
    name="toprint",
    version="0.1.32",
    description="2print/toprint: Python library for printing and converting between HTML, PDF, ZPL, and image formats with printer support. Also known as 2print or to-print.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Tom Softreck",
    author_email="info@softreck.dev",
    url="https://github.com/text2doc/toPrint",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    keywords=[
        # Podstawowe słowa kluczowe
        'printing', 'pdf', 'html', 'zpl', 'label', 'printer', 'conversion',
        
        # Warianty nazwy
        '2print', '2-print', 'print2', 'print-2', 'toprint', 'to-print',
        
        # Konwersje HTML
        'html2print', 'html-to-print', 'html2pdf', 'html-to-pdf',
        'html2zpl', 'html-to-zpl', 'html2img', 'html-to-image',
        'html2doc', 'html-to-doc', 'html2docx', 'html-to-docx',
        'html2md', 'html-to-md', 'html2markdown', 'html-to-markdown',
        'html2xml', 'html-to-xml', 'html2json', 'html-to-json',
        
        # Konwersje PDF
        'pdf2print', 'pdf-to-print', 'pdf2html', 'pdf-to-html',
        'pdf2zpl', 'pdf-to-zpl', 'pdf2img', 'pdf-to-image',
        'pdf2doc', 'pdf-to-doc', 'pdf2docx', 'pdf-to-docx',
        'pdf2md', 'pdf-to-md', 'pdf2markdown', 'pdf-to-markdown',
        'pdf2xml', 'pdf-to-xml', 'pdf2json', 'pdf-to-json',
        
        # Konwersje ZPL
        'zpl2print', 'zpl-to-print', 'zpl2pdf', 'zpl-to-pdf',
        'zpl2html', 'zpl-to-html', 'zpl2img', 'zpl-to-image',
        'zpl2doc', 'zpl-to-doc', 'zpl2docx', 'zpl-to-docx',
        'zpl2md', 'zpl-to-md', 'zpl2markdown', 'zpl-to-markdown',
        'zpl2xml', 'zpl-to-xml', 'zpl2json', 'zpl-to-json',
        
        # Konwersje obrazów
        'img2print', 'image-to-print', 'img2pdf', 'image-to-pdf',
        'img2html', 'image-to-html', 'img2zpl', 'image-to-zpl',
        'img2doc', 'image-to-doc', 'img2docx', 'image-to-docx',
        'img2md', 'image-to-md', 'img2markdown', 'image-to-markdown',
        'img2xml', 'image-to-xml', 'img2json', 'image-to-json',
        
        # Konwersje dokumentów
        'doc2print', 'doc-to-print', 'doc2pdf', 'doc-to-pdf',
        'doc2html', 'doc-to-html', 'doc2zpl', 'doc-to-zpl',
        'doc2img', 'doc-to-image', 'doc2docx', 'doc-to-docx',
        'doc2md', 'doc-to-md', 'doc2markdown', 'doc-to-markdown',
        'doc2xml', 'doc-to-xml', 'doc2json', 'doc-to-json',
        
        # Konwersje Markdown
        'md2print', 'markdown-to-print', 'md2pdf', 'markdown-to-pdf',
        'md2html', 'markdown-to-html', 'md2zpl', 'markdown-to-zpl',
        'md2img', 'markdown-to-image', 'md2doc', 'markdown-to-doc',
        'md2docx', 'markdown-to-docx', 'md2xml', 'markdown-to-xml',
        'md2json', 'markdown-to-json',
        
        # Dodatkowe funkcje
        'document-conversion', 'file-conversion', 'format-conversion',
        'document-processing', 'document-generation', 'report-generation',
        'label-printing', 'barcode', 'qrcode', 'thermal-printing',
        'zebra', 'zpl-printer', 'weasyprint', 'pdf-generation',
        'label-maker', 'document-automation', 'print-automation',
        'batch-printing', 'bulk-printing', 'template-printing'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Manufacturing',
        'Intended Audience :: System Administrators',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Printing',
        'Topic :: Text Processing :: Markup :: HTML',
        'Topic :: Multimedia :: Graphics :: Graphics Conversion',
        'Topic :: Office/Business :: Office Suites',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
    ],
    python_requires=">=3.7",
    install_requires=[
        'weasyprint>=53.0',
        'Pillow>=8.0.0',
        'reportlab>=3.6.0',
    ],
    project_urls={
        'Bug Reports': 'https://github.com/text2doc/toPrint/issues',
        'Source': 'https://github.com/text2doc/toPrint',
        'Documentation': 'https://github.com/text2doc/toPrint#readme',
        'Changelog': 'https://github.com/text2doc/toPrint/releases',
    },
    entry_points={
        'console_scripts': [
            'to-print=toPrint.cli:main',
        ],
    },
)
