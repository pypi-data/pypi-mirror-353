# aicourse_dist_prob_asreeman

aicourse_dist_prob_asreeman is a python package for computing simple descriptive statistics and graphing for two probability distributions: Gaussian and Binomial Distributions. This package was developed and uploaded as part of course material for the "AI Programming with Python" course done by Udacity. Scripts and modules developed using Andrew Paster's(instructor for Udacity course) scripts as a template.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install aicourse_dist_prob_asreeman.

```bash
pip install aicourse_dist_prob_asreeman
```

## Usage

```python
#For Gaussian distributions
from aicourse_dist_prob_asreeman import Gaussian

#For Binomial distributions
from aicourse_dist_prob_asreeman import Binomial


# returns mean of a Gaussian distribution
Gaussian.calculate_mean()

#returns probability density function of a Binomial distribution
Binomial.pdf(5) #input args for number of positive trials out of a dataset
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

## License

See LICENSE.txt in this package for license information.