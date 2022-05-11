function handleUser(url, method, username, email, password) {
  // create fetch request for create/update an user
  // return to previous refreshed window 
  const userJSON = {
    username: username, 
    email: email, 
    password: password,
  };

  fetch(url, {
    method: method,
    body: JSON.stringify(userJSON),
    headers: {
      'Content-Type': 'application/json',
    },
  })
  .then((response) => response.json())
  .then((responseJson) => {
    if (responseJson.success) {
      if (method === 'POST'){
        window.open(`/login`, '_self');
      }
    }
    else if (responseJson.error === 400) {
      alert(responseJson.message);
    }
  });
}

const formUserDetails = document.querySelector('#user-details');

formUserDetails.addEventListener('submit', (evt) => {
  evt.preventDefault();
  const method = document.querySelector('#method').value;
  const username = document.querySelector('#username').value;
  const email = document.querySelector('#email').value;
  const password = document.querySelector('#password').value;

  let url = "/users";
  if (method === 'PUT') {
    const user_id = document.querySelector('#user_id').value;
    url += `/${user_id}`;
  }
  console.log("url=", url)
  handleUser(url, method, username, email, password);
});