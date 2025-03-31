// 不推荐

class Person {
    constructor(name) {
        this.name = name;
    }

    person1 = {
        name: "张三",
        sayHi: () => {
            console.log(`Hi, I'm ${this.name}`); // this 指向外部，不是 person
        },
    };

    // 推荐
    person2 = {
        name: "张三",
        sayHi() {
            // 简写语法，this 正确指向 person
            console.log(`Hi, I'm ${this.name}`);
        },
    };
}

const person = new Person("张三");
person.person1.sayHi();
person.person2.sayHi();
