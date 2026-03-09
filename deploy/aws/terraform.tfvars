# AWS Variables
aws_region = "eu-central-1"
app_name   = "mentorhub"
environment = "production"

# Docker Image (замените на ваш ECR URL)
docker_image = "your-account.dkr.ecr.eu-central-1.amazonaws.com/mentorhub:latest"

# Container Settings
container_port = 8000
desired_count  = 2
cpu            = 1024
memory         = 2048

# Database
db_username = "mentorhub_admin"
db_password = "CHANGE_ME_TO_SECURE_PASSWORD"

# Application Secret
secret_key = "CHANGE_ME_TO_SECURE_SECRET_KEY"
