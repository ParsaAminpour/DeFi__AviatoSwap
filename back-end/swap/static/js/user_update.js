let $ = document
const display_secret = () => {
    // Select the HTML element: <div id="secret">
    let secret = $.getElementById("secret");
    if (secret.style.display && secret.style.display !== "none") {
      secret.style.display = "none";
    } else {
      secret.style.display = "block";
    }
  };
  
// Using an eventlistener to toggle div
const toggle = $.getElementById("toggle-secret");
toggle.addEventListener("click", () => {
  let secret = $.getElementById("secret");
  if (secret.style.display && secret.style.display !== "none") {
    secret.style.display = "none";
  } else {
    secret.style.display = "block";
  }
});

let username_input = $.querySelector('.username-edit')
let email_input = $.querySelector('.email-edit')

