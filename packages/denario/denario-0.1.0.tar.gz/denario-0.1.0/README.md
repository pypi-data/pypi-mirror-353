# Denario

Denario is a multiagent system designed to automatize scientific research

## Installation

NOT AVAILABLE YET

To install denario, just run

```bash
pip install denario
```

## Get started

Initialize a `Denario` instance and describe the data and tools to be employed.

```python
from denario import Denario, Journal

den = Denario(project_dir="project_dir")

prompt = "Analyze the experimental data stored in /path/to/data.csv using sklearn and pandas. This data includes time-series measurements from a particle detector."

den.set_data_description(prompt)
```

Generate a research idea from that data specification.

```python
den.get_idea()
```

Generate the methodology required for working on that idea.

```python
den.get_method()
```

With the methodology setup, perform the required computations and get the plots and results.

```python
den.get_results()
```

Finally, generate a latex article with the results. You can specify the journal style, in this example we choose the [APS (Physical Review Journals)](https://journals.aps.org/) style.

```python
from denario import Journal

den.get_paper(journal=Journal.APS)
```

You can also manually provide any info as a string or markdown file in an intermediate step, using the `set_idea`, `set_method` or `set_results` methods. For instance, for providing a file with the methodology developed by the user:

```python
den.set_method(path_to_the_method_file.md)
```

## App

You can run Astropilot using a GUI through the [AstropilotApp](https://github.com/AstroPilot-AI/AstroPilotApp).

Test the deployed app in [HugginFace Spaces](nope).

## Build from source

### pip

You will need python 3.12 installed.

Create a virtual environment

```bash
python3 -m venv .venv
```

Activate the virtual environment

```bash
source .venv/bin/activate
```

And install the project
```bash
pip install -e .
```

### uv

You can also install the project using [uv](https://docs.astral.sh/uv/), just running:

```bash
uv sync
```

which will create the virtual environment and install the dependencies and project. Activate the virtual environment if needed with

```bash
source .venv/bin/activate
```

## Contributing

Pull requests are welcome! Feel free to open an issue for bugs, comments, questions and suggestions.

## Citation

If you use this library please link this repository and cite [arXiv:2505.xxxxx](arXiv:x2506.xxxxx).

## License

To be chosen.
