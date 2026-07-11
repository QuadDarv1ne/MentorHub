"""
Tests for Email Notifications
Тесты для email уведомлений
"""

import pytest
from unittest.mock import patch, MagicMock
from app.utils.email import EmailService


class TestEmailService:
    """Тесты EmailService"""

    def test_email_service_init(self):
        """Тест инициализации EmailService"""
        service = EmailService()
        assert service.smtp_host is not None
        assert service.from_email is not None

    @patch('app.utils.email.smtplib.SMTP')
    def test_send_email_success(self, mock_smtp):
        """Тест успешной отправки email"""
        service = EmailService()
        service.smtp_user = 'test@example.com'
        service.smtp_password = 'password'

        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        result = service.send_email(
            to_email='recipient@example.com',
            subject='Test Subject',
            html_content='<p>Test</p>'
        )

        assert result is True
        mock_server.send_message.assert_called_once()

    @patch('app.utils.email.smtplib.SMTP')
    def test_send_email_failure(self, mock_smtp):
        """Тест неудачной отправки email"""
        service = EmailService()
        service.smtp_user = 'test@example.com'
        service.smtp_password = 'password'

        mock_smtp.side_effect = Exception('SMTP error')

        result = service.send_email(
            to_email='recipient@example.com',
            subject='Test Subject',
            html_content='<p>Test</p>'
        )

        assert result is False

    def test_send_email_no_credentials(self, caplog):
        """Тест отправки email без credentials"""
        service = EmailService()
        service.smtp_user = ''
        service.smtp_password = ''

        result = service.send_email(
            to_email='recipient@example.com',
            subject='Test Subject',
            html_content='<p>Test</p>'
        )

        assert result is False
        assert 'SMTP credentials not configured' in caplog.text


class TestNewMessageNotification:
    """Тесты уведомления о новом сообщении"""

    @patch('app.utils.email.smtplib.SMTP')
    def test_send_new_message_notification(self, mock_smtp):
        """Тест отправки уведомления о новом сообщении"""
        service = EmailService()
        service.smtp_user = 'test@example.com'
        service.smtp_password = 'password'

        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        result = service.send_new_message_notification(
            to_email='user@example.com',
            username='John',
            sender_name='Jane',
            message_preview='Hello!'
        )

        assert result is True
        mock_server.send_message.assert_called_once()


class TestCourseEnrollmentNotification:
    """Тесты уведомления о записи на курс"""

    @patch('app.utils.email.smtplib.SMTP')
    def test_send_course_enrollment_notification(self, mock_smtp):
        """Тест отправки уведомления о записи на курс"""
        service = EmailService()
        service.smtp_user = 'test@example.com'
        service.smtp_password = 'password'

        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        result = service.send_course_enrollment_notification(
            to_email='student@example.com',
            username='Student',
            course_name='Python Advanced',
            instructor_name='Mentor Name'
        )

        assert result is True


class TestPaymentConfirmationNotification:
    """Тесты подтверждения платежа"""

    @patch('app.utils.email.smtplib.SMTP')
    def test_send_payment_confirmation(self, mock_smtp):
        """Тест отправки подтверждения платежа"""
        service = EmailService()
        service.smtp_user = 'test@example.com'
        service.smtp_password = 'password'

        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        result = service.send_payment_confirmation(
            to_email='customer@example.com',
            username='Customer',
            amount=100.0,
            currency='USD',
            transaction_id='txn_123456',
            service_name='Mentoring Session'
        )

        assert result is True


class TestCeleryEmailTasks:
    """Тесты Celery задач для email"""

    def test_send_new_message_notification_task(self):
        """Тест задачи отправки уведомления о сообщении"""
        from app.tasks.celery_tasks import send_new_message_notification_task

        with patch('app.tasks.celery_tasks.email_service') as mock_email_service:
            mock_email_service.send_new_message_notification.return_value = True

            result = send_new_message_notification_task(
                to_email='user@example.com',
                username='User',
                sender_name='Sender',
                message_preview='Test message'
            )

            assert result is True
            mock_email_service.send_new_message_notification.assert_called_once()

    def test_send_course_enrollment_notification_task(self):
        """Тест задачи отправки уведомления о курсе"""
        from app.tasks.celery_tasks import send_course_enrollment_notification_task

        with patch('app.tasks.celery_tasks.email_service') as mock_email_service:
            mock_email_service.send_course_enrollment_notification.return_value = True

            result = send_course_enrollment_notification_task(
                to_email='student@example.com',
                username='Student',
                course_name='Test Course',
                instructor_name='Instructor'
            )

            assert result is True
            mock_email_service.send_course_enrollment_notification.assert_called_once()

    def test_send_payment_confirmation_task(self):
        """Тест задачи отправки подтверждения платежа"""
        from app.tasks.celery_tasks import send_payment_confirmation_task

        with patch('app.tasks.celery_tasks.email_service') as mock_email_service:
            mock_email_service.send_payment_confirmation.return_value = True

            result = send_payment_confirmation_task(
                to_email='customer@example.com',
                username='Customer',
                amount=50.0,
                currency='EUR',
                transaction_id='txn_789',
                service_name='Consultation'
            )

            assert result is True
            mock_email_service.send_payment_confirmation.assert_called_once()

    def test_task_failure_handling(self):
        """Тест обработки ошибок в задачах"""
        from app.tasks.celery_tasks import send_new_message_notification_task

        with patch('app.tasks.celery_tasks.email_service') as mock_email_service:
            mock_email_service.send_new_message_notification.side_effect = Exception('Error')

            with pytest.raises(Exception):
                send_new_message_notification_task(
                    to_email='user@example.com',
                    username='User',
                    sender_name='Sender',
                    message_preview='Test'
                )
