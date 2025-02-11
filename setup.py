from setuptools import setup, find_packages

setup(
    name='SVGtag',
    version='0.5',
    description='Generate 3D meshes from signed distance functions.',
    author='Stéphane Besnard',
    author_email='stephane.c.m.besnard@gmail.com',
    packages=find_packages(),
    install_requires=[
        'matplotlib',
        'numpy',
        'pandas',
        'fonttools>=4.48.1',
        'qrcode',
        'Pillow',
        'trimesh'
    ],
    license='MIT',
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ),
)