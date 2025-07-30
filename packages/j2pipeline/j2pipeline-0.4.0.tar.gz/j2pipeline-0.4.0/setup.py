import setuptools

with open(file='README.md', mode='r', encoding='UTF-8') as readme_file:
    readme: str = readme_file.read()

setuptools.setup(
    name='j2pipeline',
    version='0.4.0',
    description='Create LLM pipelines with ease!',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/yaz008/j2pipeline.git',
    author='Emelianov Artem',
    author_email='yaz008.yaz008@yandex.ru',
    license='MIT',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    include_package_data=True
)