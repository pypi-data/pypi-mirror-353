from setuptools import setup, find_packages

with open("README.md", "r") as f:
    page_description = f.read()

with open("requirements.txt") as f:
    requirements = [line.strip() for line in f if line.strip()]

setup(
    name="teste-operacoes",
    version="0.0.1",
    author="Rommano Moreira Mismetti",
    author_email="rommanomm@gmail.com",
    description="Um pacote Python simples para operações de teste.",
    long_description=page_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Rommanomm/teste_operacoes_project.git",
    packages=find_packages(),
    install_requires=requirements,
    python_requires='>=3.8',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Testing',
        'Topic :: Utilities'
    ],
)