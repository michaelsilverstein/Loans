# Multiloan

Quickly analyze the the total cost of paying off one or multiple loans

```python
from multiloan.loans import Loan, Payrange
import matplotlib.pyplot as plt
import seaborn as sns

principal = 1e4
rate = .05
payment = 200

# Create loan object
loan = Loan(principal, rate, payment)

# Analyze total costs from monthly payments of $100 to $1,000 a month
paylist = range(100, 1000, 100)
payrange = Payrange(loan, paylist)

sns.lineplot('amount', 'total', data=payrange.df, marker='o')
plt.show()
```
![payrange seaborn](data/figures/payrange_sns.png)


# Setup
Installation:
1. Clone this repo: `https://github.com/michaelsilverstein/Loans.git`
2. Install:
    ```bash
    cd Loans
    pip install ./
    ```
**Documentation [here](Documentation.md)**

# References and other tools
1. **https://unbury.us**: This is a great online tool that provided a lot of the inspiration for this project. It shows you the payment trajectory of multiple loans for a single monthly payment amount, as you can do with `multiloan`.

# Contributing
Contributions are most helpful by adding unit tests to the [test](test/) directory

Unit tests can be run with:

    python -m unittest