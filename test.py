import zmq
import asyncio
from SpeechTextFormatter import SpeechTextFormatter

async def main():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")

    formatter = SpeechTextFormatter()

    while True:
        # C++クライアントからのリクエストを待ち受ける
        message = socket.recv().decode('utf-8')
        print(f"Received request: {message}")

        # メッセージの整形処理を行う
        response_message = await formatter.replace_content(message)

        # 結果を送り返す
        if isinstance(response_message, str):
            socket.send_string(response_message)
        else:
            print("Error: response_message is not a string")
            socket.send_string("Error processing request")

if __name__ == "__main__":
    asyncio.run(main())
