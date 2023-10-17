const recruite = document.querySelector('textarea');
document.querySelectorAll("textarea").forEach((textarea) => {
  textarea.oninput = (e) => {
    const obj = e.target
    const maxHeight = parseInt(obj.getAttribute('maxheight'));
    if (maxHeight) {
      obj.innerText = obj.value;
      obj.style.height = 'auto';
      const height = obj.scrollHeight > maxHeight ? maxHeight : obj.scrollHeight;
      obj.style.height = `${height}px`;
    }
  }
});