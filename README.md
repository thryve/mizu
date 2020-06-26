
The point of this to easily transfer production data into local without the tedious
importing and exporting of CSV's. Used for seeing a customer's data locally and in the
event of a customer support ticket and they can't see a certain page for whatever error.

The code doesn't look the best and there might be bugs,
but I just wanted to whip this up because I was sick and tired
of manually transferring customer data over.

This will transfer ALL of the user's sample and sample_metrics.

To setup:

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`git clone git@github.com:thryve/mizu.git`

Create virtualenv

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`python3 -m venv venv`

Install all requirements:

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`pip install -r requirements.txt`



**BE SURE TO CREATE YOUR OWN ENV.SH**

What the env.sh should look like:

```
export PRODUCTION_DB=[PRODUCTION POSTGRESURL]
export LOCAL_DB=[LOCAL POSTGRESURL]
# the password that you would use to log in to that account for local testing
export GENERIC_PASSWORD=foobar 
source venv/bin/activate
```
Instantiate all environment variables and start virtual environment

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`source env.sh`

**Usage:**

`python3 app.py [--email email] [--id user_id]`

**Example:**

`python3 app.py --email foobar@gmail.com`

`python3 app.py --id 12345`


