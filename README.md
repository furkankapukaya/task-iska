# ISKA

## Environment

```bash
  cp .env-example .env
```

Configure .env 

**BILLING_TOKEN** : Billing service token
**BILLING_URL** : Billing service url
**MAX_BILLING_TRY_LIMIT** : Billing service retry count per subscription
**MAX_TASK_RETRY**  : CSV upload tasks retry count
**MAX_SMS_TRY_LIMIT** : SMS service retry count per subscription
**TASK_TIMEOUT**  : Task log timeout from cache
**SELF_CALLBACK** : Self asynchronous callback function for test purposes. When True SMS statuses will be updated to delivered from accepted by an asynchronous function after SMS service returned status accepted on reponse.

## Build with Docker-Compose

```bash
    cd ${PROJECT_ROOT}
    docker-compose up --build
```

## Run locally

Create virtual environment and install dependencies

```bash
  cd {PROJECT_ROOT}
  python3 -m venv venv
  source venv/bin/activate
  pip install -r app/requirements.txt

```

Run celery 

```bash
    cd {PROJECT_ROOT}/app/iska
    celery -A iska worker -l info --beat 
```

Run app

```bash
  python manage.py runserver
```

Run tests

```bash
  python manage.py test
```

## Tech

**App:** Python3.8, Django, Django-REST, PosgreSQL, Postgis

**Worker-Beat:** Celery (async-tasks), Redis(Broker)

## Usage
 
**Forecasts CRUD**  : http://localhost:8000/forecasts/api/v1/forecasts
**Subscriptions CRUD**  : http://localhost:8000/subscription/api/v1/subscription

#### Upload forecasts with csv

This task takes a few minutes with shared original forecasts file
```
curl --location --request POST 'http://localhost:8000/forecasts/api/v1/forecasts/upload_csv/' \
--form 'file=@"path_to_your_csv"'
```

**Response**	:

```
{
	'task_id': '7c864d7c-c624-498d-b4bb-fcf6143718db',
}
```

#### Get task status for forecasts upload

```
curl --location --request GET 'http://localhost:8000/forecasts/api/v1/forecasts/task_status/' \
--header 'Content-Type: application/json' \
--data-raw '{
    "task_id": "7c864d7c-c624-498d-b4bb-fcf6143718db"
}'
```

**Response**	:
```
{
    "task_status": "EXPIRED",
    "task_id": "7c864d7c-c624-498d-b4bb-fcf6143718db"
}
```

#### Upload new subscriptions with csv

Billing process starts when this task successfully completed. System trys to charge subscription until it reaches to error limit. After that subscription will be cancelled.

```
curl --location --request POST 'http://localhost:8000/subscriptions/api/v1/subscriptions/upload_additions_csv/' \
--form 'file=@"path_to_your_csv"'
```

**Response**  :

```
{
  'task_id': '7c864d7c-c624-498d-b4bb-fcf6143718db',
}
```


#### Upload cancelled subscriptions with csv

```
curl --location --request POST 'http://localhost:8000/subscriptions/api/v1/subscriptions/upload_cancellations_csv/' \
--form 'file=@"path_to_your_csv"'
```

**Response**  :

```
{
  'task_id': '7c864d7c-c624-498d-b4bb-fcf6143718db',
}
```

#### Upload location updates on current subscriptions with csv
This service only updates locations of subscription. In shared file there is no field to read new subscription plan. So I assumed when a subscription cancelled with service or due to unsuccessful billing actions only way to re-sub with same msisdn is deleting old subscription and recreate.

```
curl --location --request POST 'http://localhost:8000/subscriptions/api/v1/subscriptions/upload_updates_csv/' \
--form 'file=@"path_to_your_csv"'
```

**Response**  :

```
{
  'task_id': '7c864d7c-c624-498d-b4bb-fcf6143718db',
}
```

#### Get task status for subscription actions

```
curl --location --request GET 'http://localhost:8000/subscriptions/api/v1/subscriptions/task_status/' \
--header 'Content-Type: application/json' \
--data-raw '{
    "task_id": "7c864d7c-c624-498d-b4bb-fcf6143718db"
}'
```

**Response**  :
```
{
    "task_status": "EXPIRED",
    "task_id": "7c864d7c-c624-498d-b4bb-fcf6143718db"
}
```


### SMS

SMS action works only once a day but for test purposes I added an endpoint to trigger that task manually. 

http://localhost:8000/subscriptions/api/v1/subscriptions/trigger_send_sms
```
curl --location --request GET 'http://localhost:8000/subscriptions/api/v1/subscriptions/trigger_send_sms/'
```



| Status  | Definition	|
| ------------- |:-------------:|
|	PENDING	|	Task not startede yet 	|
|	STARTED	|	Task on running	|
| 	SUCCESS	|	Task successfully completed	|
| 	FAILURE	|	Task failed	|
|   EXPIRED | Task log doesn't exist or vanished |



