from setuptools import setup, find_packages

setup(
    name="toPrint",
    version="0.1.25",
    description="Print from html to pdf, zpl, image, printer: html to print, htmltoPrint, html to pdf,html2pdf, pdf to print, pdftoPrint, zpl to print,zpltoPrint, image to print,  imagetoPrint, ",
    author="Tom Softreck",
    author_email="info@softreck.dev",
    url="https://github.com/toPrint/toPrint",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
