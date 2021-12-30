# api-server
Api server for openEDX and Blockcert integration
Folder format is:

app_server/

├─ cert-tools/

├─ cert-issuer/

├─ app.py

├─ cert-verifier/

├─static/

app.py is the api server, made using flask. Folder starting with cert is the blockcert module. Static folder is for saving the issuer id .json file

## Connecting to kaleido
Get the rpc url with the credentials in node -> create app (kaleido)
Change the rpc url in the config file of cert-issuer to kaleido's rpc url along with basic authentication in the url (something like this: http://{username}:{password}@{json_rpc_url} )

## Cert generation
Change the api url to the api_server's url
