# LeftyDevKit 3D — static site served by nginx
FROM nginx:alpine
COPY index.html /usr/share/nginx/html/index.html
COPY assets /usr/share/nginx/html/assets
EXPOSE 80
