

# Dev Environment Deployment

## Prerequisite

1. Login to an devserver on AWS on the dev ai-playground account
1. switch to deplow/aws branch


## Website

1. Run Docker build to build and deploy the site. 

```
DOCKER_BUILDKIT=1 docker \
build \
-f Dockerfile.www \
-t sketch_www:dev_latest \
--build-arg SKETCH_API_ENDPOINT=qa-https://sketch-api.dev.metademolab.com \
--build-arg VIDEO_CDN_URL=https://sketch-video.dev.metademolab.com \
--build-arg ENABLE_UPLOAD=1 \
--build-arg REACT_APP_GOOGLE_ANALYTICS_ID=G-16PW6DPLTZ \
--build-arg AWS_S3_WWW_BUCKET=dev-demo-sketch-www \
--build-arg AWS_CLOUDFRONT_DISTRIBUTION=E1WRMCS3ULGCDH \
.
```