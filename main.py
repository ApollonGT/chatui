from chatui.app import ChatApp
from chatgpt import generate_response


if __name__ == "__main__":
    app = ChatApp()
    app.set_callback(generate_response)
    app.run()
