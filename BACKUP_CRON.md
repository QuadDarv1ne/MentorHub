# MentorHub Backup Cron Configuration
# Автоматическое резервное копирование

# Добавить в crontab (crontab -e):

# Ежедневный бэкап в 3:00 ночи
0 3 * * * /path/to/MentorHub/backup.sh cron >> /var/log/mentorhub_backup.log 2>&1

# Еженедельная проверка бэкапов (воскресенье в 4:00)
0 4 * * 0 /path/to/MentorHub/backup.sh verify /var/backups/mentorhub/db_backup_*.sql.gz >> /var/log/mentorhub_backup.log 2>&1

# Ежемесячная загрузка в S3 (1 число в 5:00)
0 5 1 * * /path/to/MentorHub/backup.sh upload >> /var/log/mentorhub_backup.log 2>&1
