const CART = {
           KEY: 'bkasjbdfkjasdkfjhaksdfjskd',
           contents: [],
           init(){
               //check localStorage and initialize the contents of CART.contents
               let _contents = localStorage.getItem(CART.KEY);
               if(_contents){
                   CART.contents = JSON.parse(_contents);
               }else{
                   CART.contents = [];
                   CART.sync();
               }
           },
           async sync(){
               let _cart = JSON.stringify(CART.contents);
               await localStorage.setItem(CART.KEY, _cart);
           },
           find(id){
               //find an item in the cart by it's id
               let match = CART.contents.filter(item=>{
                   if(item.uid == id)
                       return true;
               });
               if(match && match[0])
                   return match[0];
           },
           add(id){
               //add a new item to the cart
               //check that it is not in the cart already
               if(CART.find(id)){
                   CART.increase(id, 1);
               }else{
                   let arr = PRODUCTS.filter(product=>{
                       if(product.id == id){
                           return true;
                       }
                   });
                   if(arr && arr[0]){
                       let obj = {
                           id: arr[0].id,
                           title: arr[0].title,
                           qty: 1,
                           itemPrice: arr[0].price
                       };
                       CART.contents.push(obj);
                       //update localStorage
                       CART.sync();
                   }else{
                       //product id does not exist in products data
                       console.error('Invalid Product');
                   }
               }
           },
           increase(id, qty=1){
               //increase the quantity of an item in the cart
               CART.contents = CART.contents.map(item=>{
                   if(item.uid === id)
                       item.qty = item.qty + qty;
                   return item;
               });
               //update localStorage
               CART.sync()
           },
           reduce(id, qty=1){
               //reduce the quantity of an item in the cart
               CART.contents = CART.contents.map(item=>{
                   if(item.uid === id)
                       item.qty = item.qty - qty;
                   return item;
               });
               CART.contents.forEach(async item=>{
                   if(item.uid === id && item.qty === 0)
                       await CART.remove(id);
               });
               //update localStorage
               CART.sync()
           },
           remove(id){
               //remove an item entirely from CART.contents based on its id
               CART.contents = CART.contents.filter(item=>{
                   if(item.uid !== id)
                       return true;
               });
               //update localStorage
               CART.sync()
           },
           empty(){
               //empty whole cart
               CART.contents = [];
               //update localStorage
               CART.sync()
           },
           sort(field='title'){
               //sort by field - title, price
               //return a sorted shallow copy of the CART.contents array
               let sorted = CART.contents.sort( (a, b)=>{
                   if(a[field] > b[field]){
                       return 1;
                   }else if(a[field] < a[field]){
                       return -1;
                   }else{
                       return 0;
                   }
               });
               return sorted;
               //NO impact on localStorage
           },
           logContents(prefix){
               console.log(prefix, CART.contents)
           }
};
