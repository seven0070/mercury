FROM nginx:alpine

# Create non-root user (nginx already runs as nginx user in alpine)
USER nginx

WORKDIR /usr/share/nginx/html

COPY index.html .
COPY script.js .
COPY config.js .

EXPOSE 80

HEALTHCHECK CMD wget --quiet --tries=1 --spider http://localhost:80/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
