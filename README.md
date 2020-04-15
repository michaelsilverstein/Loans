# Multiloan

Quickly analyze the the total cost of paying off one or multiple (student) loans


<p align="center">
  <img width="500" height="576" src="data/figures/multiloan_home.png"></img>
</p>


`multiloan` allows you to analyze the payment schedule of a single loan, multiple loans, and how the total cost of loans varies with a provided range of recurring payments.

# Documentation
**Documentation:** In detail description of `multiloan` classes available [here](Documentation.md)

**Tutorial**: An interactive tutorial is  [here](tutorial.ipynb)

# Setup
Installation:
1. Clone this repo: `https://github.com/michaelsilverstein/Loans.git`
2. Install:
    ```bash
    cd Loans
    pip install ./
    ```

# References and other tools
1. **https://unbury.us**: This is a great online tool that provided a lot of the inspiration for this project. It shows you the payment trajectory of multiple loans for a single monthly payment amount, as you can do with `multiloan`.

# Contributing
Contributions are most helpful by adding unit tests to the [test](test/) directory

Unit tests can be run with:

    python -m unittest