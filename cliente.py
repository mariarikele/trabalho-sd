import grpc
import chat_pb2
import chat_pb2_grpc
import threading
import time

def send_messages(stub):
    while True:
        content = input("Escreva uma mensagem:\n")
        message = chat_pb2.Message(content=content)
        stub.Send(message)
        time.sleep(1)

def receive_messages(stub):
    for message in stub.Receive(chat_pb2.Message()):
        print(f"[{ message.sender_id }] escreveu: { message.content }")

def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = chat_pb2_grpc.ChatStub(channel)

    send_thread = threading.Thread(target=send_messages, args=(stub,), daemon=True)
    receive_thread = threading.Thread(target=receive_messages, args=(stub,), daemon=True)

    send_thread.start()
    receive_thread.start()

    send_thread.join()
    receive_thread.join()

if __name__ == '__main__':
    run()