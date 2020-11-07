from socketserver import TCPServer
from json import loads, dumps
from http.server import BaseHTTPRequestHandler
from Model import BitTutorModel

class Skeleton(BaseHTTPRequestHandler):

    def do_GET(self):

        if ( not self.path.startswith("/?") ):

            filename, extension = self.path[1:].split(".")

            self.send_response(200)
            self.send_header('Content-type', 'text/' + extension)
            self.end_headers()

            # Open file in the server's filesystem and read its bytes
            file = open( filename + "." + extension , "rb" ) 
            self.wfile.write(file.read())
            file.close()

    def do_POST(self):

        # Acquire data and parse it into a Python dictionary
        length = int(self.headers["Content-Length"])
        dataJSON = loads( self.rfile.read(length).decode("utf-8") )
        data = dict(dataJSON)

        # Identify operation and invoke model's corresponding operation

        # Note: All responses must include the 'operation' field so that
        # the client can identify the response 

        # User registration
        if data["operation"] == "registerUser":
            self.computeJSONresponse( { 'operation' : data["operation"], 'result' : controller.processUserRegistration(data) } )
            
        # User login 
        elif data["operation"] == "loginUser":

            # Try to login on the model
            loginResult = controller.processUserLogin(data)

            # Check if result was null. If so return false, otherwise send user data
            if (loginResult == None):
                self.computeJSONresponse( { 'operation' : data["operation"], 'result': False } )
            else:
                self.computeJSONresponse( { 'operation' : data["operation"], 'result': True, 'user' : loginResult } )


    def computeJSONresponse( self, dictionary ):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write( bytes ( dumps( dictionary ), 'utf-8') )
    

class Controller():

    def __init__( self ):
        self.__model = BitTutorModel()
    
    def processUserRegistration( self, data ):

        return self.__model.createUser( data["email"], data["fullName"], data["password"], data["age"],\
                data["maxLevel"], data["resume"], bytearray(data["image"]), data["imageExt"] )


    def processUserLogin( self, data ):
        return self.__model.authenticateUser( data["email"], data["password"] )

def main():

    #imgPointer = open( "Pres1.jpg", 'rb')
    #content = imgPointer.read()
    #imgPointer.close()

    #print(content)

    global controller
    controller = Controller()

    # Start serving
    httpd = TCPServer(("", 8080), Skeleton)
    httpd.serve_forever()


main()


