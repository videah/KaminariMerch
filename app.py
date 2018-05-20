import KaminariMerch


if __name__ == '__main__':
    app, socket = KaminariMerch.create_socketed_app()
    socket.run(app, host='0.0.0.0')
