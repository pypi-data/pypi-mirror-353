from setuptools import setup, find_packages

setup(
    name = 'aplicacion_ventas_gutierrez',
    version = '1.0.1',
    author="Emilio Gutierrez P.",
    author_email='emilio6927@gmail.com',
    description='Paquete para gestionar ventas',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://aulavirtual.camaracomercioexterior.org/courses/python-de-cero-a-experto/lectures/58981551',
    packages=find_packages(),
    install_requires = [],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    
python_requires='>=3.7'
)