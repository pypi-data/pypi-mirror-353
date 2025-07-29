import setuptools

setuptools.setup(
    name='data-core-pipelines-beam',
    version='0.0.2',
    description='TDD core project to develop Apache Beam with Python SDK',
    author='Israel Martinez @israndroid',
    packages=setuptools.find_packages(
        include=[
            'app'
            , 'app.*'
            , 'src'
            , 'src.*'
            , 'tests'
            , 'tests.*'
            ]
    ),
    install_requires=[
        'apache-beam[gcp]==2.65.0',
        # Puedes agregar otras dependencias aquí si las necesitas
    ],
    python_requires='>=3.8',
    include_package_data=True,
    zip_safe=False,
)
