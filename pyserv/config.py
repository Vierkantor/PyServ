# the hostname and port to listen on
host = 'localhost'
port = 8080
# set to True to enable more debugging options
debug = True
# will be set to True when testing
test = False

# determines the database we'll connect to
database_uri = 'postgresql:///py_databrowse'

# used to encode cookies to make them harder to steal and/or forge
secret_key = 'not secret'

# the path prepended to any static file access
# should usually be relative to the project dir
static_file_path = './static'
# path prepended to any dynamic file access (see the static/ and dynamic/ routes)
# must be writable and readable by the server!
dynamic_file_path = './dynamic'

# the users that have god powers
god_ids = {
	1,
}
