

curl --silent --show-error --fail -o /dev/stderr -w "%{http_code}" -X POST -H "Content-Type: application/x-www-form-urlencoded" -d 'uuid=123' --data-urlencode image@cropped_image.png http://localhost:5912/predictions/alphapose 
[ $? -eq 200 ]
