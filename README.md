Summary

Deploy New Model

Shared Libs

Local Testing

------------------------

Install Node Dependencies

npm install

Build Shared Libraries

chmod +x ./bin/shared.sh
./bin/shared.sh

Deploy Shared Libraries Layer

sls deploy --config shared.yml

Build And Deploy Training Model

cd models/visit-prediction/user
sls deploy --config train.yml