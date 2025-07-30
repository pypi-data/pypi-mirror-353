from setuptools import setup, find_packages

setup(
    name="simulate_damage",
    version="0.1.4",
    packages=find_packages(),
    install_requires=["biopython"],
    entry_points={
        "console_scripts": [
            "simulate_damage=simulate_damage.simulate_damage:run"
        ]
    },
    author="Andrew Tedder",
    author_email="a.tedder@bradford.ac.uk",
    description="Simulate ancient DNA deamination damage on paired-end FASTQ files",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/simulate_damage",
    project_urls={
        "Source": "https://github.com/yourusername/simulate_damage",
        "Tracker": "https://github.com/yourusername/simulate_damage/issues",
    },

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires='>=3.7',
)
