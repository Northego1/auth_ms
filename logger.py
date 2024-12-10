from contextvars import ContextVar
import logging


active_id_var: ContextVar[str] = ContextVar("active_id", default="unknown")


def configure_loggers():
    """Настройка логгеров."""
    # Логгер для служебных сообщений
    service_logger = logging.getLogger("service")
    service_logger.setLevel(logging.INFO)
    service_handler = logging.StreamHandler()
    service_handler.setFormatter(
        logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s")
    )
    service_logger.addHandler(service_handler)

    # Логгер для сообщений
    message_logger = logging.getLogger("message")
    message_logger.setLevel(logging.INFO)
    message_handler = logging.StreamHandler()
    message_handler.setFormatter(
        logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] [%(active_id)s] %(message)s"
        )
    )

    # Фильтр для добавления active_id
    class ActiveIDFilter(logging.Filter):
        def filter(self, record):
            record.active_id = active_id_var.get("unknown")
            return True

    message_logger.addFilter(ActiveIDFilter())
    message_logger.addHandler(message_handler)

    return service_logger, message_logger


service_logger, message_logger = configure_loggers()