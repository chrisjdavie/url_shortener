
## Initial setup

To run the demo server, the docker image needs to be built. This can be done with the following command from the terminal:

`docker build -t chris/flask_sqlalchemy_memcache .`

The docker image itself is around 500mb. Docker sometimes builds intermediate stages, so I'm not sure how big the whole collection ends up as. Shouldn't be more than a few Gb.

The server needs to be launched. Using `./run.sh`. It is set to run on port 5000 by default, which ip it gets can vary. The following command should show the IP address the container is assigned

`docker inspect -f '{{.NetworkSettings.IPAddress }} {{.Config.Image}}' $(docker ps -aq) | grep "chris/flask_sqlalchemy_memcache"`

This IP also needs to be put in the `url_shortener/config/demo.cfg`

Stop the server using `ctrl-c`.


## Launch the demo server

Run the script `./run.sh` from the folder. Some example tests can be found in `api_tests.md`

The demo server is set to clean up the database after each launch, this can be overridden by providing an external db server string in the config.


## Unit tests

Launch the server as above.

Find the name of the server. Using a new terminal

`docker inspect -f '{{.Name }} {{.Config.Image}}' $(docker ps -aq) | grep "chris/flask_sqlalchemy_memcache"`

The name is the first column, after the `/`

Run a bash shell in the background on the server

`docker exec -i -t <name> /bin/bash`

Move to the folder and run the python unit testing

`cd url_shortener/`
`python3 -m unittest discover`


## Cleanup

Close the server (`ctrl-c` in the terminal running it). 

Remove the docker container

`docker ps -a --no-trunc | grep "chris/flask_sqlalchemy_memcache" | awk '{print $1}' | xargs docker rm`

Delete the docker image

`docker images --no-trunc | grep "chris/flask_sqlalchemy_memcache" | awk '{print $3}' | xargs docker rmi`


## How to scale

This will be need to run behind a load balancer, with the shortening service code run on the servers - one per virtual process would work. The database needs to be some sort of distrubuted database, and the memcache should be run as an external server. 

These things, load balancers, scaling databases, and memcache-compatible servers can all be provided by AWS and probably by competitors. 

I'm not sure how to properly set up the communications between the docker containers, the load balancer, the database and the memcache server - it's a common task so should be well documented.


## Probably shouldn't have used SQLAlchemy as a key-value store

This set up ought to work, using a relational database interface as a key-value store works, but probably isn't sensible. I've never really thought about scalable key-value stores outside of caching before, and I didn't think about this while I was building the back end. 

I've not written anything like this before, so I'm not sure how sensible the whole solution is, I'd have to do quite a bit of load testing on it before I was happy with it. It should work though.


## Comments on the hash function

The minimum length of the shorten part of the url is 12 by default - that should work for ~1billion urls `(sqrt(32**12))`. The also handles hash collisions at the time it decides the shortening url, and should be able to handle a lot more, up to ~`(sqrt(32**20))`.

