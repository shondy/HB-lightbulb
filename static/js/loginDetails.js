const formLogin = document.querySelector('#login');

formLogin.addEventListener('submit', (evt) => {
  evt.preventDefault();
  const email = document.querySelector('#email').value;
  const password = document.querySelector('#password').value;
  const loginJSON = {
    email: email, 
    password: password,
  };

  fetch("/login", {
    method: 'POST',
    body: JSON.stringify(loginJSON),
    headers: {
      'Content-Type': 'application/json',
    },
  })
  .then((response) => response.json())
  .then((responseJson) => {
    if (responseJson.success) {
      window.open(`/all-ideas`, '_self');
    }
    else if (responseJson.error === 400) {
      alert(responseJson.message);
    }
  });
});