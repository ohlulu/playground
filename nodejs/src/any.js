import superjson from "superjson";

const a = {
    price: 1265481675487126341237126837354825628735673456788655263462358163546876712,
};

const jj = superjson.serialize(a);
console.log(jj);

const json = JSON.stringify(a);
console.log(json);
