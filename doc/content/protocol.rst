

Protocol
========

::

    Methods
    -------

    VIEW =                 11  # frontend: start a view on the backend
    INPUT_EVENT =          12  # frontend: notify the backend on a input event
    REDIRECT =             13  # backend:  redirect the client to another URL
    HTML =                 14  # backend:  view HTML on the web client
    DESKTOP_NOTIFICATION = 15  # backend:  issue a desktop notification


    Input events types
    ------------------

    CLICK =                21  # onClick()
    CHANGE =               22  # onChange()
    SUBMIT =               23  # form.submit()
    RESET =                24  # form.reset()
    CUSTOM =               25


    Event payloads
    --------------

    Click
        [CLICK, $DATA, $NODE_ID]
        [CLICK, $DATA, None, $TAG_NAME, $DIV_ID, $DIV_CLASS]

    Change
        [CHANGE, $DATA, $NODE_ID]
        [CHANGE, $DATA, None, $TAG_NAME, $DIV_ID, $DIV_CLASS]

    Submit
        [SUBMIT, $DATA, $NODE_ID]
        [SUBMIT, $DATA, None, $TAG_NAME, $DIV_ID, $DIV_CLASS]

    Custom
        [$NAME, $DATA, $NODE_ID]
        [$NAME, $DATA, None, $TAG_NAME, $DIV_ID, $DIV_CLASS]


    Examples
    --------

    >> [VIEW, 'example.org/foo/bar']
    >> [VIEW, 'example.org/foo/bar?foo=bar', {'foo': 'bar'}]

    << [REDIRECT, 'example.org/foo/bar', $INTERACTIVE]

    << [HTML, 'example.org/foo/bar', '<div id="foo"></div>', $INPUT_EVENTS]
    << [HTML, 'example.org/foo/bar', {'foo': {}},            $INPUT_EVENTS]

    >> [INPUT_EVENT, 'example.org/foo/bar', $EVENT_PAYLOAD]
