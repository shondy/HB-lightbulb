userFormInputs = document.querySelectorAll('.user-parameter');
userForm = document.querySelector('.user-form');

userForm.addEventListener('submit', (evt) => { 
  // go through all inputs and check if its filled out
  for (const input of userFormInputs) {
    if (input.value === null || input.value === ""){
      // if at least one input not filled out notify a user
      evt.preventDefault();
      alert("Please Fill All Field");
      break;
    }
  }
});