# TOC Project 2017

Final project of NCKU TOC cource

## Require Package
* Python 3
	*   Flask==0.12.1
	*   transitions==0.5.0
	*   pygraphviz==1.3.1
	*   python-telegram-bot==5.3.0
	**ADVANCE FEATURE NEED**
	*   requests
	*   beautifulsoup4
	*   Selenium

## Run the sever

```sh
$ python3 app.py
```


After that, `ngrok` would generate a https URL.

You should set `WEBHOOK_URL` (in app.py) to `your-https-URL/hook`.

## Finite State Machine Graph
![fsm](./img/show-fsm.png)

## Usage
The initial state is set to `user`.

Every time `user` state is triggered to `advance` to another state, it will `go_back` to `user` state after the bot replies corresponding message.

* user
	* Input: "go to state1"
		* Reply: "I'm entering state1"

	* Input: "go to state2"
		* Reply: "I'm entering state2"


## The author of template code
[Lee-W](https://github.com/Lee-W)
