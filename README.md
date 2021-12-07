
### sign up endpoint
{apple_id : user's apple id, email: @..., full_name:___}\
`curl -X POST -H "Content-Type:application/json" -d '{"apple_id":"1078918347", "email":"khaid@gmail.com", "full_namee":"khalid ALrasheed"}' 'http://127.0.0.1:5000/sign_up'`

## application endpoint
{"government_id" : "10XXXXXX", "car_id" : "XXXXXXXXX", "apple_id":"XXXXXXXXXX", "government_id_type":"id" or "iqama"}\
`curl -X POST -H "Content-Type:application/json" -d '{"government_id" : "1078918347", "car_id" : "102313154", "apple_id":"1078918347", "government_id_type":"id"}' 'http://127.0.0.1:5000/application'`
