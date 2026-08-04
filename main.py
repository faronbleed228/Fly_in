import sys
from parsing import parsing


def main():
    try:
        parsing(sys.argv[1])
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
