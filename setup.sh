echo "Building containers.."
docker-compose up --build -d
echo "Collecting static files.."
docker-compose run core pipenv run python manage.py collectstatic --clear --noinput
echo "Applying database migrations.."
docker-compose run core pipenv run python manage.py migrate
echo "Done! You may now login to the admin site at http://localhost/admin"
