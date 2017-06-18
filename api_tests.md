For these tests, I'm running the url shortener on `172.17.0.2:5000`. The ip address may vary, the instructions for finding the ip address are in `README.md`

The docker image needs to be built. From a terminal run

`docker build -t chris/flask_sqlalchemy_memcache .`

# Test shorten api

Run the server, from the terminal run the command

`./run.sh`

Launch docker container 

From terminal
`curl --data "url=http://www.google.com/" 172.17.0.2:5000/shorten_url`

Expected response
`{"shortened_url": "172.17.0.2:5000/_5CCH-6ysCoz"}`

In a web browser connect to `172.17.0.2:5000/_5CCH-6ysCoz`, should respond with a redirect to `google.com`


# Test cache failure

This needs the config to be altered.

Edit the config file (`url_shortener/config/demo.cfg`), change the following values under `[Basic]`

```
shorten_len=0
max_len=0
```
Run the server, from the terminal run the command

`./run.sh`

From terminal
`curl --data "url=http://www.google.com/" 172.17.0.2:5000/shorten_url`
`curl --data "url=http://www.bbc.com/" 172.17.0.2:5000/shorten_url`

Expected response

`"Unable to shorten url."`

Is a status 500.

Perhaps put the values back in the config file.

