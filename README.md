<div align="center">

# Python - Validate Move Azure Resources

Validates a source Azure resource group and all child resources to check for moveability support into a target resource group within a target subscription.

[![Build Status](https://github.com/AaronSaikovski/pyazvalidatemoveresources/workflows/build/badge.svg)](https://github.com/AaronSaikovski/pyazvalidatemoveresources/actions)
[![Coverage Status](https://coveralls.io/repos/github/AaronSaikovski/pyazvalidatemoveresources/badge.svg?branch=main)](https://coveralls.io/github/AaronSaikovski/pyazvalidatemoveresources?branch=main)
[![Licence](https://img.shields.io/github/license/AaronSaikovski/pyazvalidatemoveresources)](LICENSE)

</div>

## Python - Validate Move Azure Resources

Version History:

- 1.0 - Initial version to use environment variables
- 2.0 - Now uses command line arguments and better error handling, other bug fixes.
- 3.0 - Now uses modules and has limited unit testing.
- 3.0.2 - New makefile and updated github action.
- 3.0.3 - Updated to use poetry - see makefile
### Description

This script takes a Source SubscriptionID and Source ResourceGroup as parameters, analyzes the subscription/resource group.
and gathers a list of resource Ids and resources that can and cannot be moved to a Target SubscriptionID and Target ResourceGroup and reports accordingly.

**NOTE: This script just outputs findings and doesn't move any resources.**

### Software Requirements

- Python v3.10 or higher needs to be installed - https://www.python.org/
- Poetry v1.5.1 or higher needs to be installed - https://python-poetry.org/docs/#installation
- Azure CLI tools 2.48.1 or later
### Azure Setup

You must be logged into the Azure from the command line for this program to work. This program will use the CLIs current logged in identity.  
Ensure you have run the following:

```bash
az login

# Where "XXXX-XXXX-XXXX-XXXX" is your subscriptionID
az account set --subscription "XXXX-XXXX-XXXX-XXXX"
```

### Python Environment Setup:

Using the `Makefile` will setup the full virtual environment using Poetry for you

From bash, run:

```bash
# Using the Makefile to create the environment, run:
make create

# For the Makefile usage, run:
make help
```

### Usage:

```bash
poetry run python main.py --SourceSubscriptionId "XXXX-XXXX-XXXX-XXXX" --SourceResourceGroup "SourceRSG" --TargetSubscriptionId "XXXX-XXXX-XXXX-XXXX" --TargetResourceGroup "TargetRSG"
```

### Known issues and limitations

- Currently this program only supports subscriptions and resource groups under the same single tenant.
- No know bugs or known issues - if found, please report [here](https://github.com/AaronSaikovski/pyazvalidatemoveresources/issues)
