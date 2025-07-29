<!--
This file is part of Monitizer, a tool for optimizing and evaluating neural network monitors:
https://gitlab.com/live-lab/software/monitizer/

SPDX-FileCopyrightText: 2023 Stefanie Mohr

SPDX-License-Identifier: Apache-2.0
-->

# Monitizer

<img src="images/monitizer-logo.png" width="100">

We create a tool (Monitizer) that optimizes and evaluates monitors for a neural network (NN) for a specific task.

## Documentation

A full documentation is available online at https://monitizer.readthedocs.io/.
This also contains setup requirements, an installation guide, a dveloper guide and detailed explanations of the
structure of the project.

## Installation

### Install via pip

```bash
pip install monitizer
```

### Install from source

Download the repository:

```bash
git clone https://gitlab.com/live-lab/software/monitizer
cd monitizer
pip install .
```

**Note** that if you want to debug and change the code run the command ``pip install -e .`` to install in development
mode!

Finally, decide which ID-datasets you will be using (you can also do this again later) and download the datasets by
running:

```bash
monitizer --setup <dataset1> ... <datasetN> --data-folder <PATH/TO/DATA>
```

while replacing `<dataset>` with the name of a dataset that you intend to use, e.g. `./monitizer --setup MNIST CIFAR10`
and `<PATH/TO/DATA>` with a folder, where you want the raw data to be stored (default is 'data').
This will automatically download all required datasets, including the respective OOD-datasets, that monitizer needs.

A default command for downloading all implemented datasets is:

```bash
monitizer --setup ALL --data-folder data
```

Note that Imagenet must be downloaded after logging in, so Monitizer cannot take this over for you.
However, it will tell you, where to download the data and where to put it.
Visit https://www.image-net.org/challenges/LSVRC/2012/2012-downloads.php for downloading ILSVRC2012_devkit_t12.tar.gz,
ILSVRC2012_img_val.tar, and ILSVRC2012_devkit_t12.tar.gz, and put it in your data folder.

### Your first command

Run:

```bash
# assuming you are in the directory Monitizer
monitizer --evaluate --monitor-template energy --dataset MNIST --neural-network example-networks/MNIST3x100 --optimize --optimization-objective optimization-objective.ini
```

It optimizes an Energy monitor [(2)](https://link.springer.com/chapter/10.1007/978-3-030-88494-9_14) on a network
called "MNIST3x100", trained on the MNIST dataset. The optimization is random and the resulting monitor is then to be
evaluated.

## Running Tests

`python -m unittest discover -s tests`

## Lincense

Apache 2.0

### Maintainer(s)

Stefanie Mohr

### Contributers

Stefanie Mohr

Sudeep Kanav

Marta Grobelna

Muqsit Azeem

Sabine Rieder

# Citations

[1]: https://link.springer.com/chapter/10.1007/978-3-030-88494-9_14

[2]: https://proceedings.neurips.cc/paper/2020/file/f5496252609c43eb8a3d147ab9b9c006-Paper.pdf

[3]: https://arxiv.org/abs/1706.02690

[4]: https://ecai2020.eu/papers/1282_paper.pdf

If you use Monitizer, please cite

Azeem, M., Grobelna, M., Kanav, S., Křetínský, J., Mohr, S., Rieder, S. (2024). Monitizer: Automating Design and
Evaluation of Neural Network Monitors. In: Gurfinkel, A., Ganesh, V. (eds) Computer Aided Verification. CAV 2024.
Lecture Notes in Computer Science, vol 14682. Springer, Cham. https://doi.org/10.1007/978-3-031-65630-9_14

```
@InProceedings{monitizer,
    author="Azeem, Muqsit
    and Grobelna, Marta
    and Kanav, Sudeep
    and K{\v{r}}et{\'i}nsk{\'y}, Jan
    and Mohr, Stefanie
    and Rieder, Sabine",
    editor="Gurfinkel, Arie
    and Ganesh, Vijay",
    title="Monitizer: Automating Design and Evaluation of Neural Network Monitors",
    booktitle="Computer Aided Verification",
    year="2024",
    publisher="Springer Nature Switzerland",
    pages="265--279",
}
```