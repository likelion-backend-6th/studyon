const tags = get_tag_list();
let selected_tags = get_selected_tags()
selected_tags = selected_tags.filter(tag => tags.includes(tag));

document.addEventListener('DOMContentLoaded', (event) => {
  document.getElementById('id_tags').value = selected_tags.join(',', "");
  draw(tags)
})

document.querySelector("#submit").onclick = () => {
  document.querySelector('input[type="submit"]').click();
}

function get_tag_list() {
  const dataBox = document.querySelector("#tag-list")
  return [...dataBox.children].map((child) => child.innerText)
}

function get_selected_tags() {
  const dataBox = document.querySelector("#selected-tags")
  return dataBox.innerHTML.split(",")
}

function draw(tag_list) {
  const tag_box = document.getElementById('tagbox');
  tag_box.innerHTML = '';
  tag_list.forEach(tag => {
    const tag_element = document.createElement('div');
    tag_element.classList.add('inline-block', 'bg-neutral-100', 'px-2', 'py-1', 'mx-2', 'my-1', 'cursor-pointer');
    if (selected_tags.includes(tag)) {
      tag_element.classList.add('bg-neutral-300');
    }
    tag_element.innerText = tag;
    tag_element.onclick = () => {
      toggle_tag(tag_element)
    };
    tag_box.appendChild(tag_element);
  });
}

function toggle_tag(obj) {
  const checked_tags = document.getElementById('checkedbox');
  const tag = obj.innerText;
  const id_tags = document.getElementById('id_tags');
  if (selected_tags.length >= 3 && !selected_tags.includes(tag)) {
    return;
  }
  if (selected_tags.includes(tag)) {
    selected_tags.splice(selected_tags.indexOf(tag), 1);
    obj.classList.remove('bg-neutral-300');
  } else {
    selected_tags.push(tag);
    obj.classList.add('bg-neutral-300');
  }
  id_tags.value = selected_tags.join(',', "");
}

function search(target) {
  const search = target.value.trim();
  tags.forEach(tag => {
    if (createFuzzyMatcher(search).test(tag)) {
      console.log(tag);
    }
  });
  draw(tags.filter(tag => createFuzzyMatcher(search).test(tag)));
}

function createFuzzyMatcher(input) {
  const pattern = input.split('').map(ch2pattern).join('.*?');
  return new RegExp(pattern);
}

function ch2pattern(ch) {
  const offset = 44032; /* '가'의 코드 */
  // 한국어 음절
  if (/[가-힣]/.test(ch)) {
    const chCode = ch.charCodeAt(0) - offset;
    // 종성이 있으면 문자 그대로를 찾는다.
    if (chCode % 28 > 0) {
      return ch;
    }
    const begin = Math.floor(chCode / 28) * 28 + offset;
    const end = begin + 27;
    return `[\\u${begin.toString(16)}-\\u${end.toString(16)}]`;
  }
  // 한글 자음
  if (/[ㄱ-ㅎ]/.test(ch)) {
    const con2syl = {
      'ㄱ': '가'.charCodeAt(0),
      'ㄲ': '까'.charCodeAt(0),
      'ㄴ': '나'.charCodeAt(0),
      'ㄷ': '다'.charCodeAt(0),
      'ㄸ': '따'.charCodeAt(0),
      'ㄹ': '라'.charCodeAt(0),
      'ㅁ': '마'.charCodeAt(0),
      'ㅂ': '바'.charCodeAt(0),
      'ㅃ': '빠'.charCodeAt(0),
      'ㅅ': '사'.charCodeAt(0),
    };
    const begin = con2syl[ch] || ((ch.charCodeAt(0) - 12613 /* 'ㅅ'의 코드 */) * 588 + con2syl['ㅅ']);
    const end = begin + 587;
    console.log(`[${ch}\\u${begin.toString(16)}-\\u${end.toString(16)}]`)
    return `[${ch}\\u${begin.toString(16)}-\\u${end.toString(16)}]`;
  }
  // 그 외엔 그대로 내보냄
  // escapeRegExp는 lodash에서 가져옴
  console.log(ch)
  return escapeRegExp(ch);
}

function escapeRegExp(string) {
  return string.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); // $&은 일치한 문자열 전체를 의미
}
