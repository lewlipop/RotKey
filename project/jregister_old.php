<script type="text/JavaScript">
    // Form validation for basic errors
    function validateForm() {
        // Get values from form fields
        let email = document.forms["registerForm"]["femail"].value;
        let username = document.forms["registerForm"]["fname"].value;
        let pwd = document.forms["registerForm"]["fpwd"].value;
        let confirmPwd = document.forms["registerForm"]["fconfirmPwd"].value;

        // Boolean for return
        let isCorrect = true;

        // Validate email address
        let regex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/i;
        let x = document.getElementById("femailError");
        if (!regex.test(email)) {
            // Adds error message if email is incorrect
            x.innerText = "Email address is invalid";
            isCorrect = false;
        }
        else {
            // Removes error message if email is correct
            x.innerText = "";
        }

        // Validate username
        regex = /^[a-zA-Z0-9_\-]+$/i;
        x = document.getElementById("fnameError");
        if (!regex.test(username)) {
            x.innerText = "Usernames cannot have any special characters";
            isCorrect = false;
        }
        else {
            x.innerText = "";
        }

        // Checks password for:
        //      - 1 or more special character
        //      - 1 or more capital letter
        //      - 1 or more small letter
        //      - 1 or more number
        regex = /^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
        x = document.getElementById("fpwdError");
        if (!regex.test(pwd)) {
            x.innerText = "Password does not meet criteria";
            isCorrect = false;
        }
        else {
            x.innerText = "";
        }

        //Validate confirm password
        x = document.getElementById("fconfirmPwdError");
        if (pwd != confirmPwd) {
            x.innerText = "Passwords are not the same";
            isCorrect = false;
        }
        else {
            x.innerText = "";
        }

        return isCorrect;
    }

    // Checks if form is validated before submitting
    function register() {
        if (validateForm()) {
            alert("Successfully registered");
            document.getElementById("registerForm").submit();
        }
    }
</script>