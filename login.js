
const serverURL = "http://127.0.0.1:8080"

const sendObjectByPOST = ( object ) => {

    fetch( serverURL, {
        method: "POST",
        body: JSON.stringify( object ),
        headers: {"Content-type": "application/json; charset=UTF-8"}
    }) // End fetch
    .then(response => response.json())
    .then(data => { 
        
        // Identify response 
        alert( data["result"] ); 
        alert( data["operation"] ); 
        alert(JSON.stringify( data ))
    
    })

} // End sendObject

const registerUser = () => { 

    resume = document.getElementById("resume").value

    let user = {

        operation   : "registerUser",
        fullName    : document.getElementById("fullname").value,
        email       : document.getElementById("email").value, 
        password    : document.getElementById("password").value,
        maxLevel    : document.getElementById("studies").value,
        age         : document.getElementById("age").value,
        resume      : resume.length > 0 ? resume : null,
        image       : null,
        imageExt    : null

    } // End 

    selectedFile = document.getElementById("image").files[0]

    if (selectedFile) {

       let reader = new FileReader();
       let byteArray = [];

       reader.readAsArrayBuffer(selectedFile);
       reader.onloadend = function (evt) {

           if (evt.target.readyState == FileReader.DONE) {

                let arrayBuffer = evt.target.result;
                let array = new Uint8Array(arrayBuffer);

                // Push bytes
                for (let i = 0; i < array.length; i++) {
                    byteArray.push(array[i]);
                } // End for

            } // End if

            // Assign and send
            user.image = byteArray;
            user.imageExt = document.getElementById("image").value.split('.').pop();
            sendObjectByPOST(user);
            alert("Registration complete!");
            window.location = serverURL + "/sign-in.html";

       } // End onloadend

    } // End if 
    else {   
        sendObjectByPOST( user );
        alert("Registration complete!");
        window.location = serverURL + "/sign-in.html";
    } // End else 
    
} // End registerUser


const authenticateUser = () => {

    let loginUser = {

        operation   : "loginUser",
        email       : document.getElementById("email").value, 
        password    : document.getElementById("password").value,

    } // End object

    sendObjectByPOST(loginUser)

} // End authenticateUser