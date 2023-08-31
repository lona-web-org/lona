from lona_picocss import install_picocss

from lona import App

app = App(__file__)

install_picocss(app, debug=True)


if __name__ == '__main__':
    app.run(port=8080, live_reload=True)
