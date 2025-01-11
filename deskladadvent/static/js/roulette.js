const cells = 31; // или другое количество ячеек
const items = giftsData.map(gift => ({
  name: gift.name,  // Название подарка
  img: `/media/gifts/${gift.gift_img}`,  // Правильная запись для шаблонной строки
  chance: gift.chance,  // Шанс
  promocodes: gift.promocodes // Промокоды
}));

// Функция для получения подарка на основе его шанса
function getItem() {
  const totalChance = items.reduce((total, item) => total + item.chance, 0);

  const randomNumber = Math.floor(Math.random() * totalChance);

  let accumulatedChance = 0;
  for (const item of items) {
    accumulatedChance += item.chance;
    if (randomNumber < accumulatedChance) {
      return item;
    }
  }
}

function generateItems() {
  const scope = document.querySelector('.scope');
  scope.innerHTML = '<ul class="list"></ul>';

  const list = document.querySelector('.list');

  for (let i = 0; i < cells; i++) {
    const item = getItem();

    const li = document.createElement('li');
    li.setAttribute('data-item', JSON.stringify(item));
    li.classList.add('list__item');
    li.innerHTML = `<img src="${item.img}" alt="${item.name}" />`;



    list.append(li);
  }
}

let isStarted = false;
let isFirstStart = true;
let winningPromoCode = ''; // Переменная для хранения выбранного промокода

// Проверяем состояние кнопки при загрузке страницы
window.addEventListener('load', () => {
  const startButton = document.getElementById('startButton');
  const isDisabled = localStorage.getItem('startButtonDisabled');

  if (isDisabled === 'true') {
    startButton.disabled = true; // Делаем кнопку недоступной
  }
});

function start() {
  if (isStarted) return;
  else isStarted = true;

  // Сделать кнопку недоступной и сохранить состояние в localStorage
  const startButton = document.getElementById('startButton');
  startButton.disabled = true; // Отключить кнопку
  localStorage.setItem('startButtonDisabled', 'true'); // Сохранить состояние

  // Генерируем элементы только один раз при первом старте
  if (isFirstStart) {
    generateItems();
    isFirstStart = false;
  }

  const list = document.querySelector('.list');

  setTimeout(() => {
    list.style.left = '50%';
    list.style.transform = 'translate3d(-50%, 0, 0)';
  }, 0);

  const item = list.querySelectorAll('li')[15];

  list.addEventListener('transitionend', () => {
    isStarted = false;
    item.classList.add('active');
    const data = JSON.parse(item.getAttribute('data-item'));
    showWinAnimation(data); // Передаем данные победителя

    // Выводим в консоль промокоды
    console.log("Выигрыш:", data.name);
    console.log("Промокоды для этого подарка:", data.promocodes);
  }, { once: true });
}

function formatPromoCode(promoCode) {
  return promoCode.replace(/(.{3})(?=.)/g, '$1-');
}

function showWinAnimation(data) {
  const animationContainer = document.getElementById('animation-container');
  animationContainer.style.display = 'block';

  animationContainer.style.pointerEvents = 'none';
  const bottomFrameContainer = document.getElementById('bottom-frame-container');
  bottomFrameContainer.style.display = 'block';

  var animation = lottie.loadAnimation({
    container: animationContainer,
    renderer: 'svg',
    loop: false,
    autoplay: true,
    path: '/static/js/particles.json',
    rendererSettings: {
      preserveAspectRatio: 'none'
    }
  });

  animation.addEventListener('complete', function () {
    animationContainer.style.display = 'none';
    // После завершения анимации, изменяем URL
    window.location.href = 'https://t.me/Sovetnik1000'; // Замените на нужный вам URL
  });

  // Фильтруем промокоды, чтобы выбрать только не использованные
  const unusedPromoCodes = data.promocodes.filter(promoCode => !promoCode.is_used);

  // Если есть не использованные промокоды, выбираем случайный
  if (unusedPromoCodes.length > 0) {
    const randomPromoCode = unusedPromoCodes[Math.floor(Math.random() * unusedPromoCodes.length)];

    // Сохраняем выбранный промокод в переменную
    winningPromoCode = randomPromoCode;

    // Форматируем промокод с дефисами
    const formattedPromoCode = formatPromoCode(winningPromoCode.code);

    // Вставляем отформатированный промокод в элемент
    const promoCodeElement = document.getElementById('gift-promo-code');
    promoCodeElement.innerHTML = formattedPromoCode;  // Отображаем промокод

    // Отправляем запрос на сервер для обновления статуса промокода
    fetch('/gift/use_promocode/', {
      method: 'POST',
      body: new URLSearchParams({
        'promo_code': winningPromoCode.code  // Используем код промокода
      }),
    })
    .then(response => response.json())
    .then(data => {
      if (data.status === 'success') {
        console.log('Промокод успешно использован и привязан к пользователю');
      } else {
        console.log(data.message);
      }
    })
    .catch(error => console.error('Ошибка:', error));
  } else {
    console.log("Нет доступных для использования промокодов");
  }

  // После завершения анимации, сбрасываем флаг
  isAnimationInProgress = false;
}

generateItems();  // Генерируем элементы только один раз при загрузке страниц