SeizureCast
==============================

Real-time forecasting epileptic seizure using electroencephalogram

Deploy streamlit on EC2
-----------------------
1. Setup EC2 running ubuntu 18.04
Follow instructions here: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html

* Set up security group to allow streamlit port 8501 visted from private IP.

2. Git clone your app (github repo) to the server

* Install Streamlit *using sudo*
```sudo python3 -m pip install streamlit```
* Test the streamlit is installed properly. The following line should pass.
```streamlit -h```

3. Install tmux and run a session.
* new session:
`tmux new -s my_session`

* run streamlit app:
`streamlit run app.py`

* detach session by key sequence Ctrl-b + d to detach from the session

* (optional) kill all sessoins:
```tmux kill-session -a```

4. Install nginx and

* Run
``` sudo vim /etc/nginx/sites-enabled/streamlit```

* Add the following (Change `YOUR_DOMAIN_NAME_NO_SLASH` to your domain name)
```
server {
        listen 80;
        server_name YOUR_DOMAIN_NAME_NO_SLASH;  
        location /google {
                proxy_pass http://google.com/;
        }
        location / { # most important config
                proxy_pass http://localhost:8501/;
                proxy_http_version 1.1; 
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header Host $host;
                proxy_set_header Upgrade $http_upgrade;
                proxy_set_header Connection "upgrade";
                proxy_read_timeout 86400;
        }
}
```

And save it by `:wq`

* Reload nginx configures.
```
sudo nginx -s reload
```

5. Try it out.

Test `YOUR_DOMAIN_NAME/google` should point to google.com.

Test `YOUR_DOMAIN_NAME` should point to your app


Run
----
```
streamlit run app.py
```
