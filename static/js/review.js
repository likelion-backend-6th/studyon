document.querySelectorAll(".user-button").forEach((button) => {
  const dataSource = button.querySelector(".source");
  // 소스가 없다면 본인의 버튼
  if (!dataSource) return;
  button.addEventListener("click", () => {
    const modal = document.querySelector("#modal");
    const title = modal.querySelector("#modal-title");
    const reviewForm = modal.querySelector("form");
    const userName = dataSource.getAttribute("data-username");
    const url = dataSource.getAttribute("data-url");

    title.innerHTML = userName

    reviewForm.action = url
    console.log(reviewForm.action)
    // modal 표시
    modal.style.display = "flex";
  });
});

document.querySelector("#modal").addEventListener("click", (event) => {
  if (event.target === event.currentTarget) {
    const modal = document.querySelector("#modal");
    modal.style.display = "";
  }
});

document.querySelector("#modal-close").addEventListener("click", () => {
  const modal = document.querySelector("#modal");
  modal.style.display = "";
  console.log("asdf")
});

document.querySelector("#score").addEventListener("input", (event) => {
  const target = event.target;
  document.querySelector(`#star span`).style.width = `${target.value * 10}%`;
  console.log('asdf')
});