#include <zmq.hpp>
#include <string>
#include <iostream>

int main() {
    zmq::context_t context(1);
    zmq::socket_t socket(context, ZMQ_REQ);
    std::string connect_str = "tcp://localhost:5555";
    socket.connect(connect_str);

    // メッセージを送信
    std::string raw_message = "メッセージ内容";
    zmq::message_t request(raw_message.data(), raw_message.size());
    socket.send(request, zmq::send_flags::none);

    // レスポンスを受信
    zmq::message_t reply;
    auto result = socket.recv(reply, zmq::recv_flags::none);

    // 受信結果を確認
    if (result) {
        std::string reply_str(static_cast<char*>(reply.data()), reply.size());
        std::cout << "Received: " << reply_str << std::endl;
    } else {
        std::cerr << "Failed to receive message" << std::endl;
    }

    return 0;
}
