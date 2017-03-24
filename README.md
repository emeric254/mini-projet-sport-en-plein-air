# mini-projet-sport-en-plein-air

## How to install dependencies

Requirement : **python >= 3.3**

To make an easy install of all dependencies, use **pip** :

`pip install -r requirements.txt`


## How to use

### add your openWeatherMap api token

  1. move to 'connected_object_simulator'
  2. add a file **openweathermap.token** which contain your token


### launch all servers

Open three command line interfaces.

  1. Launch the redis server:

`redis-server`

  2. Launch the main server :

`python main.py`

  3. Then move to 'connected_object_simulator' and launch the connected object simulator:

`python main.py run-once`

(or use the 'start' argument if you want to run the simulator as a deamon)


## User story

### A new User story

  1. User register on the '/register' webpage
  2. User is now log in into the application and have a connected object located by default in 'Toulouse'
  3. User choose a sport
  4. User choose time when he's available to make this sport (in his current location)
  5. User also view other availability for this sport (in his current location)
  6. User can logout when he's done

### An actual user story

  1. User log in from the '/login' webpage
  2. User choose a sport
  3. ...etc...
