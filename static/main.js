const form = document.querySelector("form");
const input = document.querySelector("input");
const spinner = document.querySelector(".spinner-container");
const listContainer = document.querySelector(".product-list-container");
const emptyMessage = document.querySelector(".empty-msg");
const productList = document.querySelector("ul");

const productCardTemplate = (
  title,
  image,
  link,
  positive,
  neutral,
  negative
) => `
    <li class="list-group-item d-flex py-3 rounded">
      <div>
        <img src=${image} class="product-image" />
      </div>
      <div class="px-3">
        <a href=${link} target="_blank" class="text-decoration-none text-dark"><h5>${title}</h5></a>
        <span class="positive badge text-bg-success">${positive.toFixed(
          2
        )}%</span>
        <span class="neutral badge text-bg-secondary">${neutral.toFixed(
          2
        )}%</span>
        <span class="negative badge text-bg-danger">${negative.toFixed(
          2
        )}%</span>
      </div>
    </li>
`;

const handleSubmit = async (e) => {
  e.preventDefault();
  spinner.classList.remove("d-none");
  emptyMessage.classList.add("d-none");
  // if (productList.classList.contains("d-none"))
  //   productList.classList.add("d-none");
  listContainer.classList.add("d-none");
  productList.innerHTML = "";

  let product = input.value;

  if (!product) return alert("Enter a product to search");

  product = encodeURI(product);
  console.log(`http://127.0.0.1:5000/search?product=${product}`);

  try {
    const response = await fetch(
      `http://127.0.0.1:5000/search?product=${product}`
    );
    const data = await response.json();
    console.log(data);
    const noOfProducts = data.length;
    for (let i = 0; i < noOfProducts; i += 1) {
      const {
        product_title: title,
        product_image: image,
        link,
        positive,
        neutral,
        negative,
      } = data[i];
      productList.innerHTML += productCardTemplate(
        title,
        image,
        link,
        positive,
        neutral,
        negative
      );
      console.log(image);
    }

    input.value = "";
    spinner.classList.add("d-none");
    listContainer.classList.remove("d-none");
  } catch (error) {
    console.log(error);
    alert("Something went wrong");
  }
};
form.addEventListener("submit", handleSubmit);
