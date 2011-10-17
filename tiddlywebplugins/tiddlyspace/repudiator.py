"""
Invalidate cache manifest files every time they are requested.
"""


MANIFEST_TYPE = 'text/cache-manifest'


class Repudiator(object):
    """
    Invalidate a cache manifest file when it is loaded by
    including a the tiddlyspace version.
    """

    def __init__(self, application):
        self.application = application
        self.is_manifest = False
        self.environ = None
        self.headers = None
        self.status = None

    def __call__(self, environ, start_response):

        self.environ = environ

        def replacement_start_response(status, headers, exc_info=None):
            self.status = status
            self.headers = headers
            try:
                content_type = [value for header, value in headers
                        if header.lower() == 'content-type'][0]
            except IndexError:
                content_type = None
            if (environ['REQUEST_METHOD'] == 'GET'
                and content_type == MANIFEST_TYPE):
                self.is_manifest = True

        output_iter = self.application(environ, replacement_start_response)

        start_response(self.status, self.headers)

        for item in output_iter:
            yield item
        if self.is_manifest:
            yield '\n# Repudiation: ' + self._repudiator()

    def _repudiator(self):
        return self.environ['tiddlyweb.config']['tiddlyspace.version']
