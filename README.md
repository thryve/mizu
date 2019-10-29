
The point of this to easily transfer production data into local without the tedious
importing and exporting of CSV's. Used for seeing a customer's data locally and in the
event of a customer support ticket and they can't see a certain page for whatever error.

The code doesn't look the best and there might be bugs,
but I just wanted to whip this up because I was sick and tired
of manually transfering customer data over.


**BE SURE TO CREATE YOUR OWN ENV.SH**

What the env.sh should look like:

```
export PRODUCTION_DB=[PRODUCTION POSTGRESURL]
export LOCAL_DB=[LOCAL POSTGRESURL]
# the password that you would use to log in to that account for local testing
export GENERIC_PASSWORD=foobar 
source venv/bin/activate
```



**Usage:**

`python3 app.py [--email email] [--id id]`

**Example:**

`python3 app.py --email foobar@gmail.com`

`python3 app.py --id 12345`


