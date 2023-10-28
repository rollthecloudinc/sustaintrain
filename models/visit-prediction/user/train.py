import json
import os
from datetime import datetime
import numpy as np
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from tensorflow.keras.layers import Dense, LSTM
from tensorflow.keras.models import Sequential

class MinMaxScaler:
    def __init__(self, feature_range=(0, 1)):
        self.min, self.max = feature_range

    def fit_transform(self, data):
        self.data_min = np.min(data)
        self.data_max = np.max(data)
        return self.transform(data)

    def transform(self, data):
        scaled_data = self.min + (data - self.data_min) * (self.max - self.min) / (self.data_max - self.data_min)
        return scaled_data

    def inverse_transform(self, scaled_data):
        data = self.data_min + scaled_data * (self.data_max - self.data_min) / (self.max - self.min)
        return data

def handler(event, context):
    host = os.environ['HOST']
    region = os.environ['REGION']
    service = 'es'
    aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
    aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']

    awsauth = AWS4Auth(aws_access_key_id, aws_secret_access_key, region, service)

    os = OpenSearch(
        hosts=[{'host': host, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )

    model = Sequential()
    model.add(Dense(10, activation='relu', input_shape=(10,)))
    model.summary()

    index = 'auth0_log'

    body = {
        "from": 0, 
        "size": 1000,
        "query": {
            "bool": {
                "filter": [
                    {
                        "terms": {
                            "data.type.keyword": ["s", "sens", "scoa"]
                        }
                    },
                    {
                        "term": {
                            "data.user_id.keyword": "google-oauth2|110729003618916653324"
                        }
                    }
                ]
            }
        }
    }

    res = os.search(index=index, body=body)
    dates = [hit['_source']['data']['date'] for hit in res['hits']['hits']]
    dates = [datetime.strptime(x, '%Y-%m-%dT%H:%M:%S.%fZ').date().toordinal() for x in dates]

    data = np.array(dates).reshape(-1, 1)
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_dates = scaler.fit_transform(data)

    X, y = scaled_dates[0:len(scaled_dates)-1], scaled_dates[1:len(scaled_dates)]
    X = np.reshape(X, (X.shape[0], 1, X.shape[1]))

    model = Sequential()
    model.add(LSTM(100, input_shape=(X.shape[1], X.shape[2])))
    model.add(Dense(1))
    model.compile(loss='mae', optimizer='adam')
    model.fit(X, y, epochs=50, verbose=0)

    last_login_time = scaled_dates[-1]
    next_login_time = model.predict(np.reshape(last_login_time, (1, 1, 1)))
    next_login_time = scaler.inverse_transform(next_login_time)
    next_login_date = datetime.fromordinal(int(next_login_time[0][0]))

    print("The next login time is predicted to be:", next_login_date)

    return {
        'statusCode': 200,
        'body': json.dumps(f'The next login time