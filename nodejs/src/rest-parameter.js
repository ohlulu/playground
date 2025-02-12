function f(...a) {
  console.log(a);
  console.log(...a);
  console.log('---------------');
}

f(1, 2, 3);
f([4, 5, 6]);
f(...[7, 8, 9]);

