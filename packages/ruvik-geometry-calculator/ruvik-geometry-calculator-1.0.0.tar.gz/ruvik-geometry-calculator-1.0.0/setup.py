from setuptools import setup, find_packages

setup(
    name="ruvik-geometry-calculator",
    version="1.0.0",
    author="Rudnev Viktor",
    author_email="rudnevvictor2003@mail.ru",
    description="Библиотека для вычисления площади геометрических фигур",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(include=['geometry_calculator*']),
    install_requires=[],  # Зависимости (если есть)
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    extras_require={
        'test': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'coverage>=5.0'
        ],
    },
)