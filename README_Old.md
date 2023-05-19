## Python - Validate Move Azure Resources 


Version History:  
* 1.0 - Initial version to use environment variables  
* 2.0 - Now uses command line arguments and better error handling, other bug fixes.  
* 3.0 - Now uses modules and has limited unit testing.

### Description ###
Validates a source Azure resource group and all child resources to check for moveability support into a target resource group within a target subscription.  

This script takes a Source SubscriptionID and Source ResourceGroup as parameters, analyzes the subscription/resource group.
and gathers a list of resource Ids and resources that can and cannot be moved and reports accordingly.  

**This script just outputs findings and doesn't move any resources.**   

### Software Requirements ###
* Python 3.10.10 or later
* pip 23.0.1 or later (Future releases may use miniconda)
* Azure CLI tools 2.48.1 or later
* Python virtual environment and packages as specified in requirements.txt.  

### Azure Setup ###
You must be logged into the Azure from the command line for this program to work. This program will use the CLIs current logged in identity.  
Ensure you have run the following:
```bash
az login

# Where "XXXX-XXXX-XXXX-XXXX" is your subscriptionID
az account set --subscription "XXXX-XXXX-XXXX-XXXX"
```

### Python Environment Setup: ###
```bash
#setup the virtual environment
python3 -m venv .venv 

#activate the virtual environment
source .venv/bin/activate

#install packages
pip install -r requirements.txt

#upgrade PIP
pip install --upgrade pip
```

### Usage: ###
```bash
python3 main.py --SourceSubscriptionId "XXXX-XXXX-XXXX-XXXX" --SourceResourceGroup "SourceRSG" --TargetSubscriptionId "XXXX-XXXX-XXXX-XXXX" --TargetResourceGroup "TargetRSG"
```

### Known issues and limitations ###
* Currently this program only supports subscriptions and resource groups under the same single tenant.
* No know bugs or known issues - if found, please report [here](https://github.com/AaronSaikovski/pyazvalidatemoveresources/issues)