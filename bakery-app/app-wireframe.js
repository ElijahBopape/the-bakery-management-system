const screens = document.querySelectorAll('.screen');
const showScreen = (id) => {
  screens.forEach((screen) => screen.classList.toggle('active', screen.id === id));
  history.replaceState(null, '', `#${id}`);
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

document.querySelectorAll('a[href^="#"]').forEach((link) => {
  link.addEventListener('click', (event) => {
    const id = link.getAttribute('href').slice(1);
    if (document.getElementById(id)?.classList.contains('screen')) {
      event.preventDefault();
      showScreen(id);
    }
  });
});

document.querySelector('#login form')?.addEventListener('submit', (event) => {
  event.preventDefault();
  showScreen('home');
});

document.querySelectorAll('#home article button').forEach((button) => {
  button.addEventListener('click', () => {
    button.textContent = 'Added';
    button.disabled = true;
    button.setAttribute('aria-label', `${button.closest('article').querySelector('h4').textContent} added to order`);
  });
});

document.querySelectorAll('input[type="number"]').forEach((input) => {
  input.addEventListener('change', () => {
    if (input.value < 0 || input.value === '') input.value = 0;
  });
});

document.querySelector('#settings form')?.addEventListener('submit', (event) => {
  event.preventDefault();
  const button = event.currentTarget.querySelector('button');
  button.textContent = 'Saved';
  setTimeout(() => { button.textContent = 'Save preferences'; }, 1400);
});

const initialScreen = location.hash.slice(1);
showScreen(document.getElementById(initialScreen)?.classList.contains('screen') ? initialScreen : 'login');
