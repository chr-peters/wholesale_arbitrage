from wholesale.ui import data_loader
import dtale


def display_data():
    data = data_loader.get_data()
    d = dtale.show(data, host="localhost", open_browser=True)
    print("Hit enter to exit.")
    input()
    print("Exiting...")
    d.kill()


if __name__ == "__main__":
    display_data()
