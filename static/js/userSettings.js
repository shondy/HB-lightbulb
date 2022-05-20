const formUserDetails = document.querySelector('#user-details');

formUserDetails.addEventListener('submit', (evt) => {
  evt.preventDefault();
  if (formUserDetails.classList.contains('invalid')){
    formUserDetails.classList.remove('invalid');
    return;
  }
  
  const user_id = document.querySelector('.user_id').value;
  const username = document.querySelector('#username').value;
  const description = document.querySelector('#description').value;
  console.log(username, description);

  const url = `/users/${user_id}/details`;
  
  const userDetailsJSON = {
    username: username, 
    description: description,
  };

  // create fetch request to update the user
  fetch(url, {
    method: "PUT",
    body: JSON.stringify(userDetailsJSON),
    headers: {
      'Content-Type': 'application/json',
    },
  })
  .then((response) => response.json())
  .then((responseJson) => {
    if (responseJson.success) {
      window.location.reload();
    }
    else if (responseJson.error === 400) {
      alert(responseJson.message);
    }
  });
});

const formUserPassword = document.querySelector('#user-password');

formUserPassword.addEventListener('submit', (evt) => {
  evt.preventDefault();
  if (formUserPassword.classList.contains('invalid')){
    formUserPassword.classList.remove('invalid');
    return;
  }
  
  const user_id = document.querySelector('.user_id').value;
  const password = document.querySelector('#password').value;
  const confirmPassword = document.querySelector('#confirm-password').value;

  const url = `/users/${user_id}/password`;
  
  const userPasswordJSON = {
    password: password, 
    confirmPassword: confirmPassword,
  };

  // create fetch request to update the user
  fetch(url, {
    method: "PUT",
    body: JSON.stringify(userPasswordJSON),
    headers: {
      'Content-Type': 'application/json',
    },
  })
  .then((response) => response.json())
  .then((responseJson) => {
    if (responseJson.success) {
      window.location.reload();
    }
    else if (responseJson.error === 400) {
      alert(responseJson.message);
    }
  });
});