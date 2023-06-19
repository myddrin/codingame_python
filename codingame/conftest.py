

def pytest_configure(config):
    config.addinivalue_line(
        'markers', 'slow: mark test as performing slowly - code should be improved',
    )
