from services.backend_application import BackendApplication

from testing.tests import full_test


############# Testing ######
full_test()
############################

def main():
    application = BackendApplication()
    application.initialize()
    full_test()


if __name__ == "__main__":
    main()
