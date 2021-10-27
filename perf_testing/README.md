# Tooling

We are using https://k6.io/ as the main perf testing tools.

To run a test install the k6 cli tool and run test

```
k6 run first_test.js
```

To run multiple sessions in parallel with 4 virtual users and 30s

```
 k6 run --vus 4 --duration 30s upload_image_test.js

```

To create the profiler image use profile env file

```
docker-compose --env-file .env.profile build && docker-compose up
```
