docker network create wordpress_network1

docker run -d --name mysqldb_site1 \
  --network wordpress_network1 \
  -e MYSQL_DATABASE=wordpress \
  -e MYSQL_USER=wordpress \
  -e MYSQL_PASSWORD=wordpress \
  -e MYSQL_ROOT_PASSWORD=wordpress \
  -v /mysql-volume/db_data-site1:/var/lib/mysql \
  mysql:5.7


docker run -d --name wordpress_site1 \
  --network wordpress_network \
  -e WORDPRESS_DB_HOST=mysqldb_site1 \
  -e WORDPRESS_DB_USER=wordpress \
  -e WORDPRESS_DB_PASSWORD=wordpress \
  -e WORDPRESS_DB_NAME=wordpress \
  -v /wordpress-volume/wordpress_site1:/var/www/html \
  -p 8000:80 \
  wordpress
