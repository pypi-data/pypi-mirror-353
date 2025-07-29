from setuptools import setup, find_packages

setup(
    name='upblib-muhidin',  # Ganti dengan nama pustaka kamu
    version='0.1.0',
    description='Pustaka Python contoh',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Asep Muhidin',
    author_email='asep.muhidin@pelitabangsa.ac.id',
    url='https://github.com/asepmuhidin',  # Opsional
    packages=find_packages(),
    install_requires=[
        'pandas',
        'matplotlib',
        'seaborn',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.6',
)