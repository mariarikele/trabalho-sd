import grpc
import time
from concurrent import futures
import chat_pb2
import chat_pb2_grpc
import queue

class Chat(chat_pb2_grpc.ChatServicer):
    def __init__(self):
        self.clients_queues = {}

    def Send(self, request, context):
        client_id = context.peer()
        self.handleNewClient(client_id)

        for other_id, queue in self.clients_queues.items():
            if other_id != client_id:
                message = chat_pb2.Message(content=request.content, sender_id=client_id)
                queue.put(message)

        return request

    def Receive(self, request, context):
        client_id = context.peer()
        self.handleNewClient(client_id)

        while True:
            if not self.clients_queues[client_id].empty():
                message = self.clients_queues[client_id].get()
                yield message
            else:
                time.sleep(1)

    def handleNewClient(self, client_id):
        if client_id not in self.clients_queues:
            self.clients_queues[client_id] = queue.Queue()
            print(f'[{ client_id }] Entrou no chat.')

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ChatServicer_to_server(Chat(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print('------------------ Servidor conectado ------------------')
    server.wait_for_termination()

if __name__ == '__main__':
    serve()