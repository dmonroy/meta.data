from meta.data.pg import drop_database, create_database


def pytest_configure():
    drop_database()
    create_database()
