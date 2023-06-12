
# Combining content moderation services with graph databases & analytics to reduce community toxicity 

This is code repository for the supporting code to create a demonstration solution that combines Amazon Neptune with Comprehend, Rekognition and Transcribe. 

## Setup 
This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate vµ
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

## Install the dependencies for the Lambda Layer 

Then you need to install the packages needed for the Lambda Layer into the correct directory. Ensure you are in the root directory of this repository. 

```
$ pip install -r lambda_requirements.txt --target assets/ContentModLayer/python 
```
 
## Deploy the CDK template 

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

Lastly deploy the template to your AWS account
```
$ cdk deploy
```


## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
