import parser from 'yargs-parser';

const input = "deploy -r slpos -e staging, preivew"
const opt = {
    array: ['e'],
}
const argv = parser(input, opt)
console.log(argv)
console.log(argv._)
