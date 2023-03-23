from . import interface


def main():
    # Execute the commands on loop using the standart input&output
    i = interface.Interface()
    i.ping_thread_start()
    while(1):
        i.command(input())


if __name__ == "__main__":
    main()