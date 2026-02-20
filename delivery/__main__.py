from microbootstrap.granian_server import create_granian_server

from delivery.settings import settings


if __name__ == "__main__":
    create_granian_server("delivery.application:application", settings=settings).serve()
