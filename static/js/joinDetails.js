const formJoin = document.querySelector('#join');

formJoin.addEventListener('submit', (evt) => {
  evt.preventDefault();
  if (formJoin.classList.contains('invalid')){
    formJoin.classList.remove('invalid');
    return;
  }
  const username = document.querySelector('#username').value;
  const email = document.querySelector('#email').value;
  const password = document.querySelector('#password').value;
  const joinJSON = {
    username: username,
    email: email, 
    password: password,
  };

  fetch("/users", {
    method: 'POST',
    body: JSON.stringify(joinJSON),
    headers: {
      'Content-Type': 'application/json',
    },
  })
  .then((response) => response.json())
  .then((responseJson) => {
    if (responseJson.success) {
      alert("Thanks for registering! Please check your email to confirm your email address.")
      window.open(`/`, '_self');
    }
    else if (responseJson.error === 400) {
      alert(responseJson.message);
    }
  });
});