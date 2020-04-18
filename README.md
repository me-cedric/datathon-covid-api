# datathon-covid-api

```sh
py -m pip install -U pip pipenv
pipenv install
pipenv shell
python api.py
```


# deployment

Use a Linux container/WSL
```
rsync -av . datathon@gpuvm1v100.eastus.cloudapp.azure.com:~/Desktop/datathon-covid-api
ssh datathon@gpuvm1v100.eastus.cloudapp.azure.com "cd ~/Desktop/datathon-covid-api && sudo docker-compose up -d --remove-orphans --build"
```
