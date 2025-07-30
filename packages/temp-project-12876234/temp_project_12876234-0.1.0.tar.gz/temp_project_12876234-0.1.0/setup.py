from setuptools import setup, find_packages

setup(
    name='temp_project_12876234',
    version='0.1.0',
    author='Ваше Имя',
    author_email='you@example.com',
    description='Краткое описание',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/you/your-project',
    packages=find_packages(exclude=['tests*']),
    install_requires=[
        # зависимые пакеты, например 'requests>=2.0'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
