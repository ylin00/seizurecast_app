SeizureCast web app
==============================

Real-time forecasting epileptic seizure using electroencephalogram

This repo contents a streamlit web app monitoring the EEG stream sent to the server, and the seizure prediction made by the server. To access this app, visit seizurecast.com

Launch this web app on AWS EC2
------------------------------
1. Setup EC2 running ubuntu 18.04
        Follow instructions here: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html

      * Set up security group to allow streamlit port 8501 visted from private IP.

1. Install tmux and run a session.
    * new session:
        ```sh
        tmux new -s my_session
        ```
    * detach session by key sequence Ctrl-b + d to detach from the session
    * (optional) kill all sessoins:
        ```sh
        tmux kill-session -a
        ```    
2. Git clone your app (github repo) to the server
    * Install Streamlit *using sudo*
        ```sudo python3 -m pip install streamlit==0.62.0```
    * Test the streamlit is installed properly. The following line should pass.
        ```streamlit -h```

1. run streamlit app:
    ```sh
    streamlit run app.py
    ```

4. Install nginx 1.14
    ```sh
    sudo apt install nginx=1.14.0-0ubuntu1.9
    ```

    * Run
    ```sh
    sudo vim /etc/nginx/sites-enabled/streamlit
    ```

    * Add the following (Change `YOUR_DOMAIN_NAME_NO_SLASH` to your domain name)
        ```config
        server {
                listen 80;
                server_name www.example.com;  
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
        server {
                listen 80;
                server_name example.com;  
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

Test `www.example.com/google` should point to google.com.

Test `www.example.com` should point to your app


Run
----
```
streamlit run app.py
```
