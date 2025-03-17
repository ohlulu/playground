import parser from 'yargs-parser';

const input = "deploy -r slpos"

const argv = parser(input)
console.log(argv._)
