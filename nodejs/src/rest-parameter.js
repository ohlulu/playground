function f(...a) {
  console.log(typeof a, a);
  console.log(...a);
  console.log('---------------');
}

f(1, 2, 3);
f([4, 5, 6]);
f(...[7, 8, 9]);


const arr = Array.from([1, 2, 3]);
console.log(arr);
console.log(typeof arr);

