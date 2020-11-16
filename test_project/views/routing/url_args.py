def handle_request(requests, a, b, c):
    return """
        <h1>URL Arguments</h1>
        <div>a={}</div>
        <div>b={}</div>
        <div>c={}</div>
    """.format(a, b, c)
