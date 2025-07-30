# tex2image

[![Documentation Status](https://readthedocs.org/projects/tex2image/badge/?version=latest)](https://tex2image.readthedocs.io/en/latest/?badge=latest)

This is a simple library to generate images from tex snippets.

It uses the [standalone](https://ctan.org/pkg/standalone) latex package to
produce PDFs that are already set to an appropriate size, and then uses
[poppler](https://poppler.freedesktop.org/) to convert the PDF to an image.
You must make sure that `pdflatex` and `pdftoppm` are available for python to
execute.

## Example usage

An easy way to use this library is via Docker.

See the [`example`](./example) folder for a full example.
