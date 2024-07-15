import os


def get_local_files() -> list[str]:
    for t in os.walk():
        print(t)


def main():
    get_local_files()


if __name__ == '__main__':
    main()
