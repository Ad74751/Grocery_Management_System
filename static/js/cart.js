const CART = {
  KEY: "bkasjbdfkjasdkfjhaksdfjskd",
  contents: [],
  products_: [],
  init() {
    //check localStorage and initialize the contents of this.contents
    fetch("/products/all")
      .then((resp) => resp.json())
      .then((products) => {
        if (products) {
          products.map((prod) => {
            this.products_.push(prod);
          });
        }
      });
    let _contents = localStorage.getItem(this.KEY);
    if (_contents) {
      this.contents = JSON.parse(_contents);
    } else {
      this.contents = [];
      this.sync();
    }
  },
  async sync() {
    let _this = JSON.stringify(this.contents);
    await localStorage.setItem(this.KEY, _this);
  },
  find(id) {
    //find an item in the this by it's id
    let match = this.contents.filter((item) => {
      if (item.uid == id) return true;
    });
    if (match && match[0]) return match[0];
  },
  add(id) {
    //add a new item to the this
    //check that it is not in the this already
    if (this.find(id)) {
      this.increase(id, 1);
    } else {
      this.products_.filter((product) => {
        console.log(product)
        if (product.uid === id) {
          let obj = {
            id: product.uid,
            title: product.title,
            qty: 1,
            itemPrice: product.price,
          };
          console.log(obj);
          this.contents.push(obj);
          //update localStorage
          this.sync();
        }
      });
    }
  },
  increase(id, qty = 1) {
    //increase the quantity of an item in the this
    this.contents = this.contents.map((item) => {
      if (item.uid === id) item.qty = item.qty + qty;
      return item;
    });
    //update localStorage
    this.sync();
  },
  reduce(id, qty = 1) {
    //reduce the quantity of an item in the this
    this.contents = this.contents.map((item) => {
      if (item.uid === id) item.qty = item.qty - qty;
      return item;
    });
    this.contents.forEach(async (item) => {
      if (item.uid === id && item.qty === 0) await this.remove(id);
    });
    //update localStorage
    this.sync();
  },
  remove(id) {
    //remove an item entirely from this.contents based on its id
    this.contents = this.contents.filter((item) => {
      if (item.uid !== id) return true;
    });
    //update localStorage
    this.sync();
  },
  empty() {
    //empty whole this
    this.contents = [];
    //update localStorage
    this.sync();
  },
  sort(field = "title") {
    //sort by field - title, price
    //return a sorted shallow copy of the this.contents array
    let sorted = this.contents.sort((a, b) => {
      if (a[field] > b[field]) {
        return 1;
      } else if (a[field] < a[field]) {
        return -1;
      } else {
        return 0;
      }
    });
    return sorted;
    //NO impact on localStorage
  },
  logContents(prefix) {
    console.log(prefix, this.contents);
  },
};
